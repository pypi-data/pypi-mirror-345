import os
import torch
import warnings
import sqlite3
import gzip
from torch.utils.data import Dataset, DataLoader
from tqdm.auto import tqdm
from dataclasses import dataclass
from typing import Optional, Callable, List, Tuple
from huggingface_hub import hf_hub_download
from base_models.get_base_models import get_base_model
from utils import torch_load, print_message


@dataclass
class EmbeddingArguments:
    def __init__(
            self,
            embedding_batch_size: int = 4,
            embedding_num_workers: int = 0,
            download_embeddings: bool = False,
            download_dir: str = 'Synthyra/plm_embeddings',
            matrix_embed: bool = False,
            embedding_pooling_types: List[str] = ['mean'],
            save_embeddings: bool = False,
            embed_dtype: torch.dtype = torch.float32,
            sql: bool = False,
            embedding_save_dir: str = 'embeddings',
            **kwargs
    ):
        self.batch_size = embedding_batch_size
        self.num_workers = embedding_num_workers
        self.download_embeddings = download_embeddings
        self.download_dir = download_dir
        self.matrix_embed = matrix_embed
        self.pooling_types = embedding_pooling_types
        self.save_embeddings = save_embeddings
        self.embed_dtype = embed_dtype
        self.sql = sql
        self.embedding_save_dir = embedding_save_dir


class Pooler:
    def __init__(self, pooling_types: List[str]):
        self.pooling_types = pooling_types
        self.pooling_options = {
            'mean': self.mean_pooling,
            'max': self.max_pooling,
            'norm': self.norm_pooling,
            'median': self.median_pooling,
            'std': self.std_pooling,
            'var': self.var_pooling,
            'cls': self.cls_pooling,
        }

    def mean_pooling(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # (b, L, d) -> (b, d)
        if attention_mask is None:
            return emb.mean(dim=1)
        else:
            attention_mask = attention_mask.unsqueeze(-1)
            return (emb * attention_mask).sum(dim=1) / attention_mask.sum(dim=1)

    def max_pooling(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # (b, L, d) -> (b, d)
        if attention_mask is None:
            return emb.max(dim=1).values
        else:
            attention_mask = attention_mask.unsqueeze(-1)
            return (emb * attention_mask).max(dim=1).values

    def norm_pooling(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # (b, L, d) -> (b, d)
        if attention_mask is None:
            return emb.norm(dim=1, p=2)
        else:
            attention_mask = attention_mask.unsqueeze(-1)
            return (emb * attention_mask).norm(dim=1, p=2)

    def median_pooling(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # (b, L, d) -> (b, d)
        if attention_mask is None:
            return emb.median(dim=1).values
        else:
            attention_mask = attention_mask.unsqueeze(-1)
            return (emb * attention_mask).median(dim=1).values
    
    def std_pooling(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # (b, L, d) -> (b, d)
        if attention_mask is None:
            return emb.std(dim=1)
        else:
            attention_mask = attention_mask.unsqueeze(-1)
            return (emb * attention_mask).std(dim=1)
    
    def var_pooling(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # (b, L, d) -> (b, d)
        if attention_mask is None:
            return emb.var(dim=1)
        else:
            attention_mask = attention_mask.unsqueeze(-1)
            return (emb * attention_mask).var(dim=1)

    def cls_pooling(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # (b, L, d) -> (b, d)
        return emb[:, 0, :]

    def __call__(self, emb: torch.Tensor, attention_mask: Optional[torch.Tensor] = None): # [mean, max]
        final_emb = []
        for pooling_type in self.pooling_types:
            final_emb.append(self.pooling_options[pooling_type](emb, attention_mask)) # (b, d)
        return torch.cat(final_emb, dim=-1) # (b, n_pooling_types * d)


def pool_parti(X: torch.Tensor, attentions: Tuple[torch.Tensor], attention_mask: torch.Tensor) -> torch.Tensor:
    # X: (bs, seq_len, d)
    # attentions: num_layres of (bs, n_heads, seq_len, seq_len)
    # attention_mask: (bs, seq_len)
    bs, seq_len, _ = X.shape
    attentions = torch.stack(attentions, dim=1).float() # (bs, n_layers, n_heads, seq_len, seq_len)
    att_mask = attention_mask[:, None, None, None, :].expand(bs, 1, 1, seq_len, seq_len)
    attentions = attentions * att_mask
    attentions = attentions.mean(dim=2) # (bs, n_layers, seq_len, seq_len)
    attentions = attentions.mean(dim=1) # (bs, seq_len, seq_len)
    attentions = attentions.mean(dim=-1) # (bs, seq_len)
    X = X * attentions.unsqueeze(-1)
    attention_mask = attention_mask.unsqueeze(-1)
    return (X * attention_mask).sum(dim=1) / attention_mask.sum(dim=1) # (bs, d)


### Dataset for Embedding
class ProteinDataset(Dataset):
    """Simple dataset for protein sequences."""
    def __init__(self, sequences: List[str]):
        self.sequences = sequences

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> str:
        return self.sequences[idx]


def build_collator(tokenizer) -> Callable[[List[str]], tuple[torch.Tensor, torch.Tensor]]:
    def _collate_fn(sequences: List[str]) -> tuple[torch.Tensor, torch.Tensor]:
        """Collate function for batching sequences."""
        return tokenizer(sequences, return_tensors="pt", padding='longest', pad_to_multiple_of=8)
    return _collate_fn


class Embedder:
    def __init__(self, args: EmbeddingArguments, all_seqs: List[str]):
        self.args = args
        self.all_seqs = all_seqs
        self.batch_size = args.batch_size
        self.num_workers = args.num_workers
        self.matrix_embed = args.matrix_embed
        self.pooling_types = args.pooling_types
        self.download_embeddings = args.download_embeddings
        self.download_dir = args.download_dir
        self.save_embeddings = args.save_embeddings
        self.embed_dtype = args.embed_dtype
        self.sql = args.sql
        self.embedding_save_dir = args.embedding_save_dir

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print_message(f'Device {self.device} found')

    def _download_embeddings(self, model_name: str):
        # download from download_dir
        # unzip
        # move to embedding_save_dir
        local_path = hf_hub_download(
            repo_id=self.download_dir,
            filename=f'embeddings/{model_name}_{self.matrix_embed}.pth.gz',
            repo_type='dataset'
        )
        # unzip
        print_message(f'Unzipping {local_path}')
        with gzip.open(local_path, 'rb') as f_in:
            with open(local_path.replace('.gz', ''), 'wb') as f_out:
                f_out.write(f_in.read())
        # move to embedding_save_dir
        unzipped_path = local_path.replace('.gz', '')
        final_path = os.path.join(self.embedding_save_dir, f'{model_name}_{self.matrix_embed}.pth')
        
        if os.path.exists(final_path):
            print_message(f'Found existing embeddings in {final_path}')
            # Load downloaded embeddings
            downloaded_embeddings = torch_load(unzipped_path)
            existing_embeddings = torch_load(final_path)

            download_dtype = torch.float16
            if self.embed_dtype != download_dtype:
                print_message(f"Warning:\nDownloaded embeddings are {download_dtype} but the current setting is {self.embed_dtype}\nWhen combining with existing embeddings, this could result in unintended biases or reductions in performance")

            # Combine with existing embeddings
            print_message('Combining and casting')
            downloaded_embeddings.update(existing_embeddings)

            # Cast all embeddings to the correct dtype
            for seq in downloaded_embeddings:
                downloaded_embeddings[seq] = downloaded_embeddings[seq].to(self.embed_dtype)

            # Save the combined embeddings
            print_message(f'Saving combined embeddings to {final_path}')
            torch.save(downloaded_embeddings, final_path)
        return final_path

    def _read_sequences_from_db(self, db_path: str) -> set[str]:
        """Read sequences from SQLite database."""
        import sqlite3
        sequences = []
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT sequence FROM embeddings")
            while True:
                row = c.fetchone()
                if row is None:
                    break
                sequences.append(row[0])
        return set(sequences)

    def _read_embeddings_from_disk(self, model_name: str):
        if self.sql:
            save_path = os.path.join(self.embedding_save_dir, f'{model_name}_{self.matrix_embed}.db')
            if os.path.exists(save_path):
                conn = sqlite3.connect(save_path)
                c = conn.cursor()
                c.execute('CREATE TABLE IF NOT EXISTS embeddings (sequence text PRIMARY KEY, embedding blob)')
                already_embedded = self._read_sequences_from_db(save_path)
                to_embed = [seq for seq in self.all_seqs if seq not in already_embedded]
                print_message(f"Loaded {len(already_embedded)} already embedded sequences from {save_path}\nEmbedding {len(to_embed)} new sequences")
                return to_embed, save_path, {}
            else:
                print_message(f"No embeddings found in {save_path}")
                return self.all_seqs, save_path, {}

        else:
            embeddings_dict = {}
            save_path = os.path.join(self.embedding_save_dir, f'{model_name}_{self.matrix_embed}.pth')
            if os.path.exists(save_path):
                print_message(f"Loading embeddings from {save_path}")
                embeddings_dict = torch_load(save_path)
                print_message(f"Loaded {len(embeddings_dict)} embeddings from {save_path}")
                # Cast existing embeddings to the specified dtype
                #for seq in embeddings_dict:
                #    embeddings_dict[seq] = embeddings_dict[seq].to(self.embed_dtype)
                to_embed = [seq for seq in self.all_seqs if seq not in embeddings_dict]
                return to_embed, save_path, embeddings_dict
            else:
                print_message(f"No embeddings found in {save_path}")
                return self.all_seqs, save_path, {}

    def _embed_sequences(
            self,
            to_embed: List[str],
            save_path: str,
            embedding_model: any,
            tokenizer: any,
            embeddings_dict: dict[str, torch.Tensor]) -> Optional[dict[str, torch.Tensor]]:
        os.makedirs(self.embedding_save_dir, exist_ok=True)
        model = embedding_model.to(self.device).eval()
        torch.compile(model)
        device = self.device
        collate_fn = build_collator(tokenizer)
        print_message(f'Pooling types: {self.pooling_types}')
        if self.pooling_types[0] == 'parti':
            pooler = pool_parti
        elif not self.matrix_embed:
            pooler = Pooler(self.pooling_types)
        else:
            pooler = None

        def _get_embeddings(residue_embeddings: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
            if residue_embeddings.ndim == 2 or self.matrix_embed: # sometimes already vector emb
                return residue_embeddings
            else:
                return pooler(residue_embeddings, attention_mask)

        dataset = ProteinDataset(to_embed)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, num_workers=self.num_workers, collate_fn=collate_fn, shuffle=False)

        if self.sql:
            conn = sqlite3.connect(save_path)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS embeddings (sequence text PRIMARY KEY, embedding blob)')

        with torch.no_grad():
            for i, batch in tqdm(enumerate(dataloader), total=len(dataloader), desc='Embedding batches'):
                seqs = to_embed[i * self.batch_size:(i + 1) * self.batch_size]
                input_ids, attention_mask = batch['input_ids'].to(device), batch['attention_mask'].to(device)
                if self.pooling_types[0] == 'parti':
                    try:
                        residue_embeddings, attentions = model(input_ids, attention_mask, output_attentions=True)
                        embeddings = pooler(residue_embeddings, attentions, attention_mask).cpu()
                    except Exception as e:
                        print_message(f"Error in parti pooling: {e}\nDefaulting to mean pooling")
                        self.pooling_types = ['mean']
                        pooler = Pooler(self.pooling_types)
                        residue_embeddings = model(input_ids, attention_mask)
                        embeddings = pooler(residue_embeddings, attention_mask).cpu()
                else:
                    residue_embeddings = model(input_ids, attention_mask)
                    embeddings = _get_embeddings(residue_embeddings, attention_mask).cpu()

                for seq, emb, mask in zip(seqs, embeddings, attention_mask.cpu()):
                    if self.matrix_embed:
                        emb = emb[mask.bool()]
                    
                    if self.sql:
                        c.execute("INSERT OR REPLACE INTO embeddings VALUES (?, ?)", 
                                (seq, emb.numpy().tobytes())) # only supports float32
                    else:
                        embeddings_dict[seq] = emb.to(self.embed_dtype)
                
                if (i + 1) % 100 == 0 and self.sql:
                    conn.commit()

        if self.sql:
            conn.commit()
            conn.close()
            return None
        
        if self.save_embeddings:
            print_message(f"Saving embeddings to {save_path}")
            torch.save(embeddings_dict, save_path)
            
        return embeddings_dict

    def __call__(self, model_name: str):
        if self.download_embeddings:
            self._download_embeddings(model_name)

        if self.device == 'cpu':
            warnings.warn("Downloading embeddings is recommended for CPU usage - Embedding on CPU will be extremely slow!")
        to_embed, save_path, embeddings_dict = self._read_embeddings_from_disk(model_name)
        
        if len(to_embed) > 0:
            print_message(f"Embedding {len(to_embed)} sequences with {model_name}")
            model, tokenizer = get_base_model(model_name)
            return self._embed_sequences(to_embed, save_path, model, tokenizer, embeddings_dict)
        else:
            print_message(f"No sequences to embed with {model_name}")
            return None


if __name__ == '__main__':
    ### Embed all supported datasets with all supported models
    import argparse
    from huggingface_hub import upload_file, login
    from data.supported_datasets import possible_with_vector_reps
    from data.data_mixin import DataArguments, DataMixin
    from base_models.get_base_models import BaseModelArguments, get_base_model

    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1' # prevent cache warning on Windows machines

    parser = argparse.ArgumentParser()
    parser.add_argument('--token', default=None, help='Huggingface token')
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--num_workers', type=int, default=0)
    parser.add_argument('--embed_dtype', type=str, default='float16')
    parser.add_argument('--embedding_save_dir', type=str, default='embeddings')
    parser.add_argument('--download_dir', type=str, default='Synthyra/mean_pooled_embeddings')
    parser.add_argument('--compress', default=True, action='store_true', help='Compress embeddings with gzip before uploading')
    args = parser.parse_args()

    if args.token is not None:
        login(args.token)

    if args.embed_dtype == 'float16':
        dtype = torch.float16
    elif args.embed_dtype == 'bfloat16':
        dtype = torch.bfloat16
    elif args.embed_dtype == 'float32':
        dtype = torch.float32
    else:
        raise ValueError(f"Invalid embedding dtype: {args.embed_dtype}")

    # Get data    
    data_args = DataArguments(
        data_names=possible_with_vector_reps,
        max_length=2048,
        trim=False
    )
    all_seqs = DataMixin(data_args).get_data()[1]

    # Set up embedder
    embedder_args = EmbeddingArguments(
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        download_embeddings=False,
        matrix_embed=False,
        pooling_types=['mean'],
        save_embeddings=True,
        embed_dtype=dtype,
        sql=False,
        embedding_save_dir='embeddings'
    )
    embedder = Embedder(embedder_args, all_seqs)

    # Embed for each model
    model_args = BaseModelArguments(model_names=['standard'])
    for model_name in model_args.model_names:
        _ = embedder(model_name)
        save_path = os.path.join(args.embedding_save_dir, f'{model_name}_False.pth')
        
        # Compress file if requested
        if args.compress:
            compressed_path = f"{save_path}.gz"
            print(f"Compressing {save_path} to {compressed_path}")
            with open(save_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            upload_path = compressed_path
            path_in_repo = f'embeddings/{model_name}_False.pth.gz'
        else:
            upload_path = save_path
            path_in_repo = f'embeddings/{model_name}_False.pth'
            
        upload_file(
            path_or_fileobj=upload_path,
            path_in_repo=path_in_repo,
            repo_id=args.download_dir,
            repo_type='dataset'
        )

    print('Done')