"""Training pipeline module for SubFluxGPT."""

# Lazy imports to avoid requiring all dependencies for basic module import
__all__ = ['PretokDataset', 'Task', 'get_tokenizer_model_path', 'TrainingScheduler', 'GPT2Trainer']

def __getattr__(name):
    if name == 'PretokDataset':
        from training_pipeline.bugbounty import PretokDataset
        return PretokDataset
    if name == 'Task':
        from training_pipeline.bugbounty import Task
        return Task
    if name == 'get_tokenizer_model_path':
        from training_pipeline.bugbounty import get_tokenizer_model_path
        return get_tokenizer_model_path
    if name == 'TrainingScheduler':
        from training_pipeline.scheduler import TrainingScheduler
        return TrainingScheduler
    if name == 'GPT2Trainer':
        from training_pipeline.train_gpt2 import GPT2Trainer
        return GPT2Trainer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
