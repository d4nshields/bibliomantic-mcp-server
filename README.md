# Bibliomantic MCP Server

> **Tired of watching your LLM queries wander down the wrong path because of random hallucinations?**
>
> Why leave the randomness entirely to the model?

**bibliomantic-mcp-server** gives an LLM a different source of uncertainty: randomly selected context drawn from the *I Ching*.

The inspiration comes from Philip K. Dick's science-fiction novel *The Man in the High Castle*. Throughout the novel, characters consult the *I Ching* when making decisions. Its influence extends beyond the characters themselves: the oracle affects the direction of the story, the fictional book within the story, and—famously—the process Philip K. Dick used while writing the novel.

This MCP server applies that idea to an LLM.

Rather than asking the model to simply invent another direction when reasoning or writing reaches an uncertain point, the user can explicitly invoke the server to introduce an *I Ching* consultation into the model's context. The resulting hexagram becomes an external, stochastic influence that the LLM can interpret and incorporate into whatever it is doing.

In other words:

**If your LLM is going to hallucinate anyway, you might as well give its hallucinations some ancient Chinese wisdom to work with.**

The server operates **only when invoked by the end user or an MCP client acting on the user's request**. It is not intended to autonomously interfere with ordinary model responses.

And, importantly, this project does **not** claim that the *I Ching* predicts the future or provides reliable real-world advice. It is an experimental, literary, philosophical, and creative-writing tool—particularly suitable for anyone curious about what happens when an AI system is allowed to wander through the same sort of bibliomantic machinery that helped shape a Philip K. Dick novel.

## What Is This?

**bibliomantic-mcp-server** is a Model Context Protocol server that allows an MCP-compatible AI application to consult the *I Ching*.

It provides:

* All 64 hexagrams, with traditional texts for a growing subset (see [Content Coverage](#content-coverage))
* Three-coin divination simulation
* Randomized bibliomantic context for LLM reasoning and writing
* Individual hexagram lookup
* MCP resources containing hexagram data
* Structured consultation tools designed for AI use

The interesting part is not merely generating a hexagram.

The interesting part is putting that hexagram **inside an LLM's context** and seeing what the model does with it.

## The Idea

Large language models are probabilistic systems. When confronted with ambiguity, incomplete information, creative choices, or multiple plausible reasoning paths, they must choose among possibilities.

Normally, those choices emerge entirely from the model itself.

Bibliomantic MCP introduces an additional influence.

```text
User question
     │
     ▼
    LLM
     │
     │ user requests bibliomantic consultation
     ▼
bibliomantic-mcp-server
     │
     ▼
three-coin I Ching simulation
     │
     ▼
hexagram + interpretation
     │
     ▼
added to LLM context
     │
     ▼
LLM continues with a new influence
```

The oracle does not replace the model's reasoning.

It perturbs it.

That makes the server potentially interesting for:

* creative writing
* speculative reasoning
* brainstorming
* narrative generation
* alternative perspectives
* experiments involving stochastic AI behavior
* literary experiments inspired by Philip K. Dick

## Philip K. Dick and *The Man in the High Castle*

The central inspiration for this project is Philip K. Dick's *The Man in the High Castle*.

The *I Ching* occupies an unusual position in the novel. Characters repeatedly consult it when deciding what to do, allowing apparently random divinations to alter their actions and therefore the course of the story.

The idea becomes recursive.

The novel contains a fictional novel, *The Grasshopper Lies Heavy*, whose existence influences the characters living inside Dick's alternate history. Meanwhile, Dick himself used the *I Ching* while writing *The Man in the High Castle*.

The result is an unusual feedback loop between:

* author
* oracle
* story
* characters
* story-within-the-story

**bibliomantic-mcp-server explores what happens when an LLM is inserted into that loop.**

Instead of:

```text
Author → I Ching → Story
```

we can now experiment with:

```text
Human → LLM → I Ching → LLM → Story
```

## A Note About "Hallucinations"

The term *hallucination* is used somewhat playfully here.

This server does **not** technically prevent LLM hallucinations, improve factual accuracy, or make unreliable model output trustworthy.

In fact, its purpose is almost the opposite.

Bibliomantic MCP deliberately introduces an external, randomly selected conceptual influence when the user asks for one.

For factual questions, this may be completely inappropriate.

For fiction, brainstorming, speculative thinking, and experiments in AI creativity, however, deliberately steering the model toward an unexpected conceptual path can be the entire point.

## Available Tools

### `i_ching_divination`

Performs an *I Ching* divination using a simulated traditional three-coin method and returns the resulting hexagram and interpretation.

### `bibliomantic_consultation`

Performs a complete bibliomantic consultation intended to provide additional context for an LLM responding to a particular question or creative problem.

### `get_hexagram_details`

Retrieves information about a particular *I Ching* hexagram by number.

```text
1–64
```

How much traditional text comes back depends on the hexagram — see [Content Coverage](#content-coverage).

### `server_statistics`

Returns information about the server and its available capabilities.

## Resources

### `hexagram://{number}`

Loads a particular hexagram as an MCP resource.

For example:

```text
hexagram://1
```

### `iching://database`

Provides access to the complete 64-hexagram database.

## Content Coverage

All 64 hexagrams carry an English name, Unicode symbol, trigram analysis and a summary
interpretation. Authored traditional text is still being filled in, so entries fall into
three tiers:

| Tier | Hexagrams | What it carries |
| --- | --- | --- |
| `full` | 1, 2 | Chinese name, judgment, image, per-line texts, contextual readings and commentary |
| `traditional` | 11, 63 | Chinese name, judgment and image |
| `summary` | the other 60 | English name, Unicode symbol, trigrams and a summary interpretation |

Where a traditional text has not been authored, **the server omits that section and says
so** rather than substituting generated wording. A consultation on a `summary` hexagram
therefore has no Judgment, Image or Traditional Commentary block, and its summary is
labelled as an editorial paraphrase rather than a translation. Changing lines are still
calculated for all 64 by the three-coin method; only the per-line *texts* are limited to
the `full` tier.

Call `server_statistics` for live counts — they are read from the data set, not hardcoded.

## Prompt Templates

The server includes structured prompt templates for several forms of consultation:

* `career_guidance_prompt`
* `creative_guidance_prompt`
* `general_guidance_prompt`

These templates provide examples of how an MCP client can incorporate bibliomantic context into a larger conversation.

They should not be interpreted as endorsements of the *I Ching* as a source of professional or real-world advice.

## Installation & Configuration

Choose one of the methods below to connect the Bibliomantic server to your MCP host (such as Claude Desktop).

### Option 1: Modern & Automatic (Recommended)
If you have [uv](https://github.com/astral-sh/uv) installed, you do not need to clone or manually install anything. `uvx` fetches the package from GitHub, installs it into a cached environment and runs the `bibliomantic-mcp-server` entry point.

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bibliomantic": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/d4nshields/bibliomantic-mcp-server",
        "bibliomantic-mcp-server"
      ]
    }
  }
}
```

Every divination result carries a short ethical guidance note that the assistant conveys in context. To omit it, add `"--no-ethical-disclaimers"` as a final entry in `args` (see [Ethical Disclaimers](#ethical-disclaimers)).

To pin to a specific commit instead of following `main`, append `@<commit-sha>` to the URL, e.g. `git+https://github.com/d4nshields/bibliomantic-mcp-server@44a2bdc`.

## ⚠️ Security & Supply Chain Notice

Model Context Protocol (MCP) servers run with local system permissions granted by your AI host (like Claude Desktop). Running servers directly from remote sources introduces security risks. 

Before installing or running *any* MCP server:
1. **Audit the Source:** Review the codebase to ensure it contains no malicious scripts or unexpected network behaviors.
2. **Understand the Risk of Direct Remote Execution:** Using tools like `uvx --from git+https://...` means you are executing the latest code directly from the web. If a repository is compromised, malicious code could execute on your machine.
3. **Use Content Hashes/Pins:** For maximum security, pin your configurations to specific git commit hashes rather than floating branches like `main`.


---

### Option 2: Local STDIO Setup (Manual Environment)
If you prefer to run the server entirely on your local machine using standard I/O (STDIO), follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/d4nshields/bibliomantic-mcp-server.git
   cd bibliomantic-mcp-server
   ```

2. **Install the package:**
   You can install it using `pip` (ideally within a virtual environment):
   ```bash
   pip install .
   ```
   *(Alternatively, use `pip install -r requirements.txt` if you prefer tracking individual dependencies.)*

3. **Configure your host:**
   Add the server to your local configuration file. Make sure to replace `path/to/your/python` with the actual path to your environment's Python executable:

   ```json
   {
     "mcpServers": {
       "bibliomantic": {
         "command": "/path/to/your/python",
         "args": ["-m", "bibliomantic_server"]
       }
     }
   }
   ```

   Append `"--no-ethical-disclaimers"` to `args` if you do not want disclaimers in responses.
   
   
## Example Usage

### Creative writing

Ask your MCP-enabled AI:

> I'm stuck on what should happen next in this story. Consult the I Ching and use the result as an influence on the next scene.

### Breaking a reasoning deadlock

> There are several plausible ways to approach this fictional problem. Perform a bibliomantic consultation and use the result to choose an unexpected direction to explore.

### Philip K. Dick-style experiment

> Consult the I Ching using the bibliomantic server. Treat the result as an external influence on the direction of this science-fiction story.

### Basic divination

> Perform an I Ching divination and explain the resulting hexagram.

### Specific hexagram

> Tell me about I Ching hexagram 42.

## How the Divination Works

The server simulates the traditional three-coin method.

Coin tosses generate the six lines forming an *I Ching* hexagram. The resulting pattern identifies one of the 64 hexagrams available to the model.

Randomness is generated using Python's `secrets` module.

The important distinction is that the random result is generated **outside the LLM**.

That means the model does not get to quietly choose the supposedly "random" piece of wisdom that happens to fit the answer it was already constructing.

The MCP server chooses first.

The LLM has to deal with what it gets.

That constraint is a significant part of the experiment.

## Why External Randomness?

An LLM asked to "pick something random" is still generating tokens according to its learned probability distribution.

Bibliomantic MCP instead introduces a result produced outside the model.

This creates a simple form of stochastic context injection:

```text
LLM state
   +
externally generated random event
   +
structured I Ching interpretation
   =
new model context
```

The result can push a conversation toward concepts or associations that might otherwise have had very low probability of appearing.

For creative applications, that can be useful.

Or at least interesting.

## User Control

Bibliomantic consultation is intended to be **explicitly invoked**.

The server does not need to participate in every query and should not silently inject divinations into unrelated conversations.

A user might work normally with an LLM for an extended period and invoke the oracle only when they want:

* an unexpected direction
* a narrative disruption
* an alternative interpretation
* a creative constraint
* a deliberate random influence

This keeps the oracle in approximately the role it occupies in *The Man in the High Castle*: something consulted when a character—or in this case, a user—decides to consult it.

## Ethical Disclaimers

The server appends a short guidance note to each `i_ching_divination`, `bibliomantic_consultation` and `get_hexagram_details` result. The note is addressed to the assistant, not quoted to you. It asks the assistant to make sure you understand, in its own words:

* the hexagram was chosen by secure randomness, not supernatural guidance
* it is a prompt for reflection and entertainment, not a prediction
* for financial, medical, legal or safety decisions you should consult a qualified professional

The assistant is asked to fit this to the question: a light touch for a casual reading, an explicit caution when a serious decision is involved. The same request is repeated in the server's MCP `instructions` field.

Because an MCP tool result is read by the model, which then writes its own reply, the server can ask for this but cannot enforce it. To see the raw note, expand the tool call in your MCP host.

This is **on by default**. Turn it off by starting the server with:

```bash
python -m bibliomantic_server --no-ethical-disclaimers
```

or by adding `"--no-ethical-disclaimers"` to the `args` list in your MCP host configuration. `server_statistics` reports whether disclaimers are currently enabled.

Internally the note is applied by a `@with_disclaimer()` decorator in `bibliomantic_server/ethics.py`, so the tool bodies contain no disclaimer text themselves. The design and its trade-offs are recorded in [ADR-002](docs/ADR-002-contextual-ethical-guidance.md).

## Intended Uses

Good uses include:

* Science-fiction writing
* Philip K. Dick-inspired literary experiments
* Plot generation
* Character decisions
* World-building
* Creative brainstorming
* Perspective shifting
* Generative-art experiments
* Studying human/AI interaction with random external context
* Demonstrating MCP tools and resources

## Not Intended For

Do not treat output from this server as authoritative guidance for:

* medical decisions
* legal decisions
* financial decisions
* personal safety
* mental-health treatment
* major life decisions
* predictions of future events

The server does not establish that divination works, that an oracle possesses knowledge, or that randomly selected philosophical text provides factual evidence.

**This is an experimental creative tool, not an oracle you should bet your life on.**

If Philip K. Dick-style weirdness emerges from your LLM session, however, the software is probably working as intended.

## Technical Implementation

The project uses:

* **Python**
* **MCP Python SDK (`MCPServer`)**
* **Model Context Protocol**
* A 64-hexagram data set (traditional text coverage is partial and reported at runtime)
* Python's `secrets` module for external randomness
* Type hints and generated schemas
* MCP tools, resources, and prompts

The server requires no external API to perform a consultation.

## Development

### Run locally

```bash
python -m bibliomantic_server
python -m bibliomantic_server --no-ethical-disclaimers    # without disclaimers
python -m bibliomantic_server --help
```

### MCP Inspector

```bash
mcp dev bibliomantic_server/main.py
```

## Security and Privacy

The server is deliberately simple.

* No persistent user tracking
* No requirement to transmit consultations to an external divination service
* No external API dependency for generating random results
* Input validation for server parameters
* Randomness generated locally
* Consultation occurs only when invoked

As with any MCP server, users should review the source code and understand the permissions granted to an MCP server before enabling it in an AI host.

## Contributing

Contributions are welcome.

When contributing:

1. Follow the existing code style.
2. Preserve compatibility with MCP clients.
3. Add or update tests when changing behavior.
4. Update documentation when adding tools or resources.
5. Preserve the distinction between creative bibliomancy and factual or professional advice.
6. Keep the weird part weird.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

This project owes its existence to an unusual chain of ideas:

* the ancient Chinese *I Ching*
* centuries of bibliomantic practice
* Philip K. Dick
* *The Man in the High Castle*
* modern large language models
* Model Context Protocol
* and the questionable but irresistible idea that an AI's random wanderings might benefit from consulting a 3,000-year-old book first.

---

**The model was going to take *some* path.**

**Now the oracle gets a vote.**
