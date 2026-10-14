# config/finetune_hackerone.py
# Fine-tune GPT-2 on HackerOne subdomain/DNS/takeover reports

import time

out_dir = "out-hackerone-subdomains"

eval_interval = 50
eval_iters = 20
log_interval = 10

wandb_log = False
wandb_project = "hackerone-subdomains"
wandb_run_name = "ft-" + str(time.time())

# Must match the folder data/hackerone/
dataset = "hackerone"

# Fine-tune pretrained GPT-2 weights; gpt2 is lighter than gpt2-xl.
init_from = "gpt2"

# Save the best checkpoint based on validation loss.
always_save_checkpoint = True

batch_size = 1
gradient_accumulation_steps = 8
max_iters = 500

# Fine-tuning learning rate.
learning_rate = 1e-5
decay_lr = True
warmup_iters = 50
lr_decay_iters = 500
min_lr = 1e-6

# Keep the pretrained GPT-2 context length.
block_size = 1024
