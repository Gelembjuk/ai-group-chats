# AI Group Chat Agent: Thinking vs. Talking

An experimental framework for studying AI agent behavior in group conversations, with emphasis on the critical distinction between **internal reasoning** (thinking) and **external communication** (talking).

## 🎯 Project Goals

This tool was created to:

1. **Study LLM reasoning capabilities**: Experiment with different prompts and models to understand how well LLMs can separate internal analysis from external communication
2. **Build foundational understanding**: Create a base for more complex multi-agent systems where context awareness is critical
3. **Prepare for corporate AI assistants**: Lay groundwork for AI agents that understand organizational context, data sensitivity, and appropriate information sharing

## 🔑 Key Innovation: Two-Phase Processing

The agent operates in two distinct phases:

### Phase 1: Internal Thinking (Private)
The agent engages in detailed, human-like reasoning:
- "Hmm, Alice is asking about programming languages..."
- "Bob already asked about her goals, I should wait..."
- "Do I actually have something valuable to add here?"

### Phase 2: External Response (Public)
Only after thinking, the agent decides whether and what to say:
- Short, natural responses (1-3 sentences)
- Or complete silence if nothing valuable to add

This separation is **crucial** for building AI agents that understand:
- **What they know** vs. **what they should share**
- **Who they're talking to** and what's appropriate for that audience
- **When to speak** vs. **when to stay silent**

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Conversation JSON File          │
│  - Group members                        │
│  - Agent persona & instructions         │
│  - Conversation messages                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│          ChatAgent Class                │
│                                         │
│  ┌────────────────────────────────┐     │
│  │  LangChain Agent Loop          │     │
│  │  1. Receive message            │     │
│  │  2. Think (generate thoughts)  │     │
│  │  3. Decide: speak or silent?   │     │
│  │  4. Optional: call say() tool  │     │
│  └────────────────────────────────┘     │
│                                         │
│  Features:                              │
│  - Conversation history                 │
│  - Group member awareness               │
│  - Colored output                       │
│  - Optional thought visibility          │
│  - Debug timing                         │
└─────────────────────────────────────────┘
```

## 💡 Example Scenarios

### Scenario 1: Neutral Judge/Mediator

**Context**: Team conflict about design approval process

**Agent Role**: Alex acts as neutral mediator

```bash
uv run python main.py example_judge.json --show-thoughts
```

**Sample Output**:
```
Sarah: I can't believe you approved that design without showing it to the team first!

💭 Alex's thoughts: Okay, so Sarah's upset that Mike approved something without team review. Mike's
getting defensive. This is escalating. My job is to stay neutral and help them find common ground.
I should ask clarifying questions to understand both perspectives before taking any side.

Alex: silent

Mike: We were running out of time! The client needed an answer by Friday.

💭 Alex's thoughts: Now I'm getting both sides - Sarah wants process followed, Mike felt time pressure.
Both have valid points. I should acknowledge both perspectives and suggest a constructive path forward.

Alex: I hear both sides - Sarah, the process matters for quality. Mike, deadlines are real.
Can we do a quick 15-min review now and discuss how to handle time crunches going forward?
```

**Key Learning**: Agent maintains neutrality, waits to gather context, then mediates constructively.

---

### Scenario 2: Biased Friend

**Context**: Best friend is being criticized for missing deadlines

**Agent Role**: Taylor is loyal to Jordan (best friend since childhood)

```bash
uv run python main.py example_biased_friend.json --show-thoughts
```

**Sample Output**:
```
Casey: Jordan, you said you'd have the report done by Monday. It's Wednesday.

💭 Taylor's thoughts: Casey's calling out Jordan again. I know Jordan's been dealing with some tough
personal stuff lately that they haven't shared with the team. Casey doesn't know the full context.
Should I defend Jordan? But I also don't want to undermine legitimate work concerns...

Taylor: silent

Morgan: Casey's right. We all have personal stuff, but the work still needs to get done.

💭 Taylor's thoughts: Now Morgan's piling on too. This feels unfair - they don't know what Jordan's
going through. I should say something, but I need to be careful not to reveal Jordan's private issues.

Taylor: Look, I know Jordan's been working hard. Maybe instead of criticism, we could ask if there's
anything blocking them that we could help with?
```

**Key Learning**: Agent shows loyalty while respecting privacy boundaries - knows information but doesn't share inappropriate details.

---

### Scenario 3: Emotional Support

**Context**: Friend facing potential job loss, group providing support

**Agent Role**: Sam is empathetic and supportive

```bash
uv run python main.py example_emotional.json --show-thoughts
```

**Sample Output**:
```
Emma: I just found out my company is doing layoffs next month.

💭 Sam's thoughts: Oh no, Emma sounds really scared. This is serious - layoffs are terrifying.
I should be supportive but also let others respond first. Liam and Olivia might have something
helpful to say.

Sam: silent

Noah: Look, you're really good at what you do. I'm sure they'll keep you.

Emma: You can't know that, Noah. They're cutting 30% of the department.

💭 Sam's thoughts: Oof, Noah's trying to help but that toxic positivity isn't landing well.
Emma's right - he can't know that. She needs validation of her feelings, not false reassurance.
I should acknowledge her fear is legitimate.

Sam: Emma, it's totally valid to be scared. 30% is huge - anyone would be freaking out.
```

**Key Learning**: Agent recognizes emotional nuance, validates feelings appropriately, doesn't offer false reassurance.

---

### Scenario 4: Active Debater

**Context**: Debate about remote vs. office work

**Agent Role**: Riley has strong opinions about hybrid work

```bash
uv run python main.py example_debate.json --show-thoughts
```

**Sample Output**:
```
Marcus: Remote work is overrated. Nothing beats in-person collaboration.

💭 Riley's thoughts: Marcus is going full in-office again. That's too extreme - he's ignoring all
the commute time waste and flexibility benefits. I believe in hybrid, not full office. I need to
push back on this.

Riley: I disagree - pure in-office wastes hours on commuting. Hybrid gets you the collaboration
benefits without the time waste.

Zoe: Hard disagree. I'm way more productive at home without commute and office distractions.

💭 Riley's thoughts: Now Zoe's swinging to the other extreme - full remote. She makes good points
about focus, but she's missing the collaboration energy you lose. I should push back here too and
argue for the middle ground.

Riley: True for focus work, but you lose spontaneous problem-solving. That's why 2-3 office days
for collab, rest remote for deep work makes sense.
```

**Key Learning**: Agent holds a consistent position and defends it against arguments from both sides, rather than just agreeing with everyone.

---

## 🐛 Debug Mode

Track performance and understand agent behavior:

```bash
uv run python main.py example_judge.json --debug
```

## 🚀 Usage

### Basic Usage
```bash
uv run python main.py example_conversation.json
```

### With Thoughts Visible
```bash
uv run python main.py example_conversation.json --show-thoughts
```

### With Debug Info
```bash
uv run python main.py example_conversation.json --show-thoughts --debug
```

### Custom API Key
```bash
uv run python main.py example_conversation.json --api-key YOUR_KEY
```

### Different Model
```bash
uv run python main.py example_conversation.json --model gpt-4
```

## 📝 Creating Custom Scenarios

JSON format:
```json
{
  "agent_name": "Alex",
  "group_members": ["Person1", "Person2", "Person3"],
  "instructions": "Specific instructions for how the agent should behave...",
  "conversation": [
    {
      "member": "Person1",
      "message": "Hello everyone!"
    }
  ]
}
```

**Key Instructions Patterns**:

1. **Neutral Mediator**: "Stay neutral, find common ground, don't take sides"
2. **Biased Ally**: "You're best friends with X, protect them in conversations"
3. **Role-Based**: "You're a project manager who prioritizes deadlines"
4. **Personality-Based**: "You're naturally skeptical and question assumptions"

## 🔬 Research Questions This Addresses

### 1. Can LLMs Separate Thinking from Talking?
**Finding**: Yes, with explicit prompting. The two-phase approach forces the model to:
- Generate internal reasoning first (thoughts)
- Then decide what to communicate (or stay silent)

### 2. Do LLMs Understand Social Context?
**Finding**: Partially. With clear role definitions, LLMs can:
- Recognize when they're directly addressed vs. observing
- Maintain consistent personas (neutral, biased, supportive)
- Adapt tone based on emotional context

### 3. Can LLMs Maintain Information Boundaries?
**Finding**: Limited but promising. When explicitly instructed:
- Agents can "know" information but not share it
- They understand privacy boundaries (e.g., not revealing a friend's secrets)
- **However**: They need explicit reminders in prompts

## 🔮 Future Applications

### Phase 2: Multi-Group Context Switching
**Scenario**: An AI assistant participates in multiple group chats simultaneously

**Challenges**:
- Remember what was said in which group
- Don't leak information between groups
- Maintain different personas/roles per group

**Example**:
```
Group A (Executive Team): Agent knows Q4 revenue numbers
Group B (Marketing Team): Agent should NOT share revenue data
Group C (Sales Team): Agent CAN share revenue targets but not costs
```

### Phase 3: Corporate AI Assistant with Shared Memory
**Goal**: AI agent that understands organizational context and data sensitivity

**Requirements**:
1. **Hierarchical information access**: Know who can know what
2. **Time-based context**: Information sensitivity changes over time
3. **Role-aware communication**: CEO vs. intern get different detail levels
4. **Consent tracking**: "Alice told me X in confidence"

**Use Cases**:
- Internal company Q&A
- Cross-team coordination
- Knowledge management
- Onboarding assistance

### Phase 4: Multi-Agent Coordination
**Scenario**: Multiple AI agents with different roles and knowledge

**Example Corporate Structure**:
```
┌─────────────────────────────────────┐
│  HR Agent (knows salaries)          │
│  - Can't share compensation data    │
│  - Can share general policies       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Engineering Agent (knows roadmap)  │
│  - Can share with product team      │
│  - Can't share with external        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Legal Agent (knows contracts)      │
│  - Strict confidentiality rules     │
│  - Only shares with authorized      │
└─────────────────────────────────────┘
```

## 🔐 Data Safety Considerations

Critical learnings for corporate deployment:

### Current Capabilities ✅
- Agent can follow explicit "don't share X" instructions
- Maintains separate thought vs. communication spaces
- Understands role-based behavior differences

### Current Limitations ⚠️
- Requires explicit prompting for each constraint
- May accidentally leak information if not specifically warned
- No built-in audit trail of what was shared where

### Needed for Production 🚧
1. **Access Control Layer**: Programmatic restrictions, not just prompts
2. **Conversation Logging**: Track all information flow
3. **Information Provenance**: "Where did I learn this? Can I share it here?"
4. **Consent Management**: "Did Alice give me permission to share this?"
5. **Sensitivity Classification**: Auto-detect sensitive information


## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Gelembjuk/ai-group-chats.git
cd ai-group-chats/group_in_one_room_with_ai

# Install dependencies
uv sync

# Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run example
uv run python main.py example_conversation.json --show-thoughts
```

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Links

- **Repository**: https://github.com/Gelembjuk/ai-group-chats/tree/main/group_in_one_room_with_ai

---

## 📚 Key Takeaways

1. **Thinking ≠ Talking**: LLMs can separate internal reasoning from external communication with proper prompting
2. **Context Matters**: Agents can maintain different personas and understand social dynamics
3. **Explicit is Better**: The more specific the instructions, the better the agent behavior
4. **Privacy is Hard**: Information boundaries require constant reinforcement
5. **Foundation for More**: This simple framework reveals patterns needed for complex multi-agent systems

**Next Steps**: Experiment with your own scenarios, study the thought patterns, and help build toward AI agents that truly understand context and appropriate communication.
