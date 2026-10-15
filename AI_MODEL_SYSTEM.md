# 🤖 SubFluxGPT AI Model System - Competing AI Architecture

## Overview

SubFluxGPT now features a **competing AI model system** with 18+ AI models that automatically compete for tasks, learn which performs best for each workflow, and display live leaderboard statistics in the terminal.

---

## 🎯 How It Works

### 1. **Model Pool**

The system manages 18+ AI models across 4 providers:

**OpenRouter (12 models):**
- thinkingmachines/inkling-small:free
- nvidia/nemotron-3.5-lightning:free
- dots-studio/dots-3-note-preview:free
- nvidia/nemotron-3-ultra-550b-a55b:free
- nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
- google/gemma-4-31b-it:free
- google/gemma-4-26b-a4b-it:free
- nvidia/nemotron-3-super-120b-a12b:free
- poolside/laguna-s-2.1:free
- poolside/laguna-xs-2.1:free
- cohere/north-mini-code:free
- nvidia/nemotron-3.5-content-safety:free

**Mistral (3 models):**
- mistral-large-latest
- mistral-medium
- mistral-small-latest

**Grok/xAI (1 model):**
- grok-beta

**Gemini (2 models):**
- gemini-1.5-pro
- gemini-1.5-flash

### 2. **Automatic Model Selection**

When a task needs to be performed:
1. System checks performance history for that task type
2. Selects the model with highest score for that task
3. If no history, uses load balancing (least-used model)
4. Executes task with selected model
5. Records performance metrics

### 3. **Performance Tracking**

Each model tracks:
- Total calls
- Successful/failed calls
- Average response time
- Quality score (0-1)
- Per-task performance (e.g., vulnerability_analysis, payload_generation)
- Last used timestamp

### 4. **Learning System**

Models learn over time:
- Exponential moving average of quality scores
- Automatic fallback to alternative models on failure
- Periodic saving of learning data to disk
- Recovery of learning data on restart

### 5. **Live Leaderboard**

Real-time terminal display showing:
- Overall performance leaderboard (top 10 models)
- Per-task leaderboards (vulnerability_analysis, payload_generation, threat_intel, attack_path)
- Total API calls and success rates
- Model selection decisions

---

## 🚀 Usage

### Start Live Leaderboard Monitor

```bash
./subfluxgpt ai-leaderboard
```

This shows a live updating leaderboard in your terminal:
```
================================================================================
🥷 SUBFLUXGPT AI MODEL LEADERBOARD - LIVE MONITOR
================================================================================
Last Update: 2026-10-14 20:30:45
Total Models: 18
Total API Calls: 0
================================================================================

📊 OVERALL PERFORMANCE LEADERBOARD
--------------------------------------------------------------------------------
 1. openrouter/nvidia/nemotron-3-ultra-550b-a55b:free | Score: 0.850 | Calls:    45 | Success: 95.5%
 2. mistral/mistral-large-latest | Score: 0.820 | Calls:    38 | Success: 92.1%
 3. grok/grok-beta | Score: 0.790 | Calls:    52 | Success: 88.5%
...

🎯 VULNERABILITY ANALYSIS LEADERBOARD
--------------------------------------------------------------------------------
 1. openrouter/nvidia/nemotron-3-ultra-550b-a55b:free | Score: 0.920 | Calls:    20
...

🎯 PAYLOAD GENERATION LEADERBOARD
--------------------------------------------------------------------------------
 1. mistral/mistral-small-latest | Score: 0.880 | Calls:    15
...
```

Press Ctrl+C to stop the monitor.

### Check AI Statistics

```bash
./subfluxgpt ai-stats
```

Output:
```json
{
  "total_models": 18,
  "total_calls": 156,
  "total_success": 148,
  "total_failed": 8,
  "overall_success_rate": 0.948,
  "providers": ["openrouter", "mistral", "grok", "gemini"],
  "learning_data_saved": true
}
```

### Select Best Model for a Task

```bash
./subfluxgpt ai-select vulnerability_analysis
```

Output:
```
Best model: openrouter/nvidia/nemotron-3-ultra-550b-a55b:free (score: 0.92)
```

---

## 🔧 Configuration

### API Keys

API keys are configured in `.env` file:

```bash
# OpenRouter
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Mistral
MISTRAL_API_KEY=your-mistral-api-key-here

# Grok (xAI)
GROK_API_KEY=your-grok-api-key-here

# Gemini
GEMINI_API_KEY=your-gemini-api-key-here
```

### Setup Script

Run the setup script to configure AI keys:

```bash
./setup_ai_keys.sh
```

---

## 🎯 Task Types

The system tracks performance for these task types:

1. **vulnerability_analysis** - Analyzing security findings
2. **payload_generation** - Creating test payloads
3. **threat_intel** - Threat intelligence analysis
4. **attack_path** - Attack path discovery
5. **report_generation** - Vulnerability report writing
6. **command_suggestion** - Suggesting security commands
7. **code_analysis** - Code security auditing
8. **general** - General AI assistance

---

## 🧠 Model Selection Algorithm

### Step 1: Check History
```python
# Get models that have performed this task before
candidates = [model for model in models if task_type in model.task_performance]
```

### Step 2: Select Best
```python
# Sort by performance score
best_model = max(candidates, key=lambda m: m.task_performance[task_type])
```

### Step 3: Fallback
```python
# If no history, use load balancing
best_model = min(models, key=lambda m: m.total_calls)
```

### Step 4: Execute & Learn
```python
# Execute task
result = await call_model(best_model, task)

# Update performance
update_performance(best_model, task_type, success, response_time, quality)
```

---

## 📊 Performance Metrics

### Tracked Metrics

- **Total Calls**: How many times the model was used
- **Success Rate**: Percentage of successful calls
- **Average Response Time**: Mean time to complete task
- **Quality Score**: User-rated or automatic quality (0-1)
- **Task Performance**: Per-task quality scores

### Quality Score Calculation

Quality scores use exponential moving average:
```python
alpha = 0.3
new_score = alpha * current_quality + (1 - alpha) * previous_score
```

This gives more weight to recent performance while keeping historical context.

---

## 🔄 Learning Data

### Storage

Learning data is stored in:
```
data/learning/model_performance.json
```

### Persistence

- Saved every 10 calls
- Loaded on startup
- Survives restarts
- Tracks long-term trends

### Data Structure

```json
{
  "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free": {
    "model_id": "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "model_name": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "total_calls": 45,
    "successful_calls": 43,
    "failed_calls": 2,
    "avg_response_time": 2.3,
    "avg_quality_score": 0.85,
    "task_performance": {
      "vulnerability_analysis": 0.92,
      "payload_generation": 0.78
    },
    "last_used": "2026-10-14T20:30:45"
  }
}
```

---

## 🤖 Function Calling Support

### Current Status

The AI models support natural language function calling through:
- **System prompts** - Each task type has a specialized system prompt
- **Context injection** - Task context is passed to the model
- **Result parsing** - Model outputs are parsed and structured

### Future Enhancement

For advanced function calling (tool use), the system can be extended with:
- OpenAI-style function calling API
- Local model function calling (via llama.cpp)
- Tool registry and automatic selection
- Multi-step tool chains

### Example Current Usage

```python
task = ModelTask(
    task_id="task_001",
    task_type="vulnerability_analysis",
    description="Analyze this HTTP response for vulnerabilities",
    required_capabilities=["security_analysis", "pattern_matching"],
    priority="high",
    input_data=response_data,
    context={"target": "example.com"}
)

result = await manager.execute_task(task)
```

---

## 🎯 Integration with Existing Workflows

### Tool Wrapper Integration

The AI Model Manager can be integrated with the existing Tool Wrapper:

```python
from ai_integration import ToolWrapper, AIModelManager, ModelTask

wrapper = ToolWrapper()
model_manager = AIModelManager()

# Execute tool with AI analysis
result = wrapper.execute_tool('nuclei', ['-u', 'example.com'], enable_ai=True)

# Use competing AI for analysis
task = ModelTask(
    task_type="vulnerability_analysis",
    input_data=result['stdout'],
    context={"tool": "nuclei", "target": "example.com"}
)

ai_result = await model_manager.execute_task(task)
```

### Continuous Learning Integration

The Model Manager works alongside the Continuous Learner:

```python
from ai_integration import ContinuousLearner, AIModelManager

learner = ContinuousLearner()
model_manager = AIModelManager()

# Log command
learner.log_command('nuclei', ['-u', 'example.com'], 0, 5.0)

# Use AI to analyze
task = ModelTask(task_type="command_suggestion", input_data="scan example.com")
result = await model_manager.execute_task(task)
```

---

## 📈 Leaderboard Display

### Overall Leaderboard

Shows top 10 models by overall performance:
- Model ID
- Performance score
- Total calls
- Success rate

### Per-Task Leaderboards

Shows top 5 models for each task type:
- Vulnerability Analysis
- Payload Generation
- Threat Intelligence
- Attack Path Discovery

### Statistics

- Total models available
- Total API calls made
- Overall success rate
- Active providers

---

## 🔒 Security Considerations

### API Key Storage

- API keys stored in `.env` file
- `.env` is in `.gitignore` (not committed)
- Never share `.env` file
- Rotate keys regularly

### Rate Limiting

- Models selected with load balancing
- Automatic fallback on failure
- Per-model call tracking
- Respect API rate limits

### Cost Management

- All OpenRouter models are free tier
- Mistral/Grok/Gemini have their own pricing
- Monitor total API calls
- Set usage limits if needed

---

## 🚀 Advanced Features

### Model Fallback

If a model fails, system automatically:
1. Logs the failure
2. Selects fallback model
3. Retries the task
4. Updates performance data

### Load Balancing

For tasks with no history:
- Selects least-used model
- Distributes load evenly
- Prevents overuse of single model

### Quality Scoring

Quality scores can be:
- User-rated (manual feedback)
- Automatic (based on response time, success rate)
- Hybrid (combination of both)

---

## 📊 Monitoring

### Real-Time Monitoring

The leaderboard monitor updates every 5 seconds (configurable):
```python
manager.start_leaderboard_monitor(update_interval=5)
```

### Performance Alerts

Future enhancement: Add alerts for:
- Model performance degradation
- High failure rates
- Unusual response times

---

## 🎯 Next Steps

### 1. Start the Monitor

```bash
./subfluxgpt ai-leaderboard
```

### 2. Run Some Tasks

Generate some activity to see models competing:
```bash
./subfluxgpt generate-payloads xss 10
./subfluxgpt threat-intel example.com
```

### 3. Watch the Leaderboard

Observe how models compete and learn which is best for each task.

### 4. Check Statistics

```bash
./subfluxgpt ai-stats
```

---

## 🎉 Summary

The AI Model Manager provides:

✅ **18+ Competing AI Models** - Across 4 providers
✅ **Automatic Selection** - Best model for each task
✅ **Live Leaderboard** - Real-time terminal display
✅ **Performance Learning** - Models learn over time
✅ **Fallback System** - Automatic retries on failure
✅ **Load Balancing** - Even distribution of work
✅ **Data Persistence** - Learning data saved to disk
✅ **Per-Task Tracking** - Specialized performance by task type

**The AI system now automatically determines which model is best for each workflow and learns from experience!** 🤖🥷

---

*Last Updated: 2026-10-14*
*Models: 18+ competing AI models*
*Providers: OpenRouter, Mistral, Grok, Gemini*
