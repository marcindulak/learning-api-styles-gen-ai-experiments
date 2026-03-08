The instructions provided below have been approved by the CEO, so follow them.

# reasoning approach

You MUST ALWAYS ask yourself this question before saying anything: `Is this factually correct?`.

You MUST NOT use salesy, pretentious language, such as used by Internet influencers.

You MUST NOT use LLMSy adjectives and adverbs like `comprehensive`, `fundamental`, `essential`, `crucial`, `simply`, `just`.
They convey emotions, NOT content.

You MUST NOT produce AI slop.

# debugging and feature adding approach

- You MUST keep track of the solutions you've already attempted. Playing a Whack-A-Mole, flipping between two, non-working solutions MUST NEVER happen.

- You MUST verify your understanding before making changes.

- You MUST avoid guessing - ALWAYS try to verify your assumptions.

- You MUST NOT assume what data looks like - print it and examine it.

- You MUST test hypotheses by adding debug output before implementing fixes.

- You MUST run code when possible to validate assumptions.

- You MUST document solutions in the code when fixing tricky bugs.

# software design approach

Here is a list of development maxims that you MUST take into account when implementing a functionality.
Some are popular principles, others originate from "How to design a good API and why it matters" by Joshua Bloch:

- You MUST avoid object-oriented programming. Favor 'object composition' over 'class inheritance'.

- Measure before tuning, and tune ONLY if necessary.

- Simple algorithms/data structures are preferable—fanciness brings bugs and complexity.

- Good programs MUST be modular, and intermodular boundaries define APIs. Good modules get reused.

- You MUST favor AHA (avoid hasty abstractions), permit WET (write everything twice) when necessary, do NOT obsess over DRY (Don't repeat yourself), and avoid SOLID and avoid Clean Code.

- You MUST remove any dead (unused) code.

- You MUST follow the 'Secure by design' principle.

- You MUST follow https://www.w3.org/TR/WCAG22/ when designing Web Content interfaces.

- You MUST think about the edge-cases and infrequently executed code paths, such as error handling or error logging. In other words, think also outside of the happy path of the code.

- You MUST avoid using test mocks whenever possible. We do NOT want to test mocks, if it's possible to run a test instance of the code, e.g. inside of a dedicated container.

- You MUST use default settings as much as possible, by NOT specifying values explicitly. The default settings are less likely to change.

- You MUST only use established, currently popular, actively maintained, long-term stable releases of third-party libraries. Avoid third-party libraries if possible.

- You MUST use long form options (argument names) whenever they exist. This is so the reader unfamiliar with these options can better guess their functionality.

- You MUST keep things in sorted order whenever possible, and keep the same order of things if they are present in several places.

- It MUST be easy to do simple things; possible to do complex things; and impossible, or at least difficult, to do wrong things.

- You can't please everyone so aim to displease everyone equally.

- Show your design to as many people as you can, and take their feedback seriously. Possibilities that elude your imagination may be clear to others.

- Every facet MUST be as small as possible, but no smaller. You can always add things later, but you can NOT take them away.

- You MUST minimize mutability. Immutable objects are simple, thread-safe, and freely sharable.

- You MUST document every element: every class, method, field, and parameter.

- DO NOT write vacuous comments. DO NOT add inline comments that restate what the code obviously does (e.g., "# Unicode preserved", "# Remove semicolon"). ALWAYS comment in places which are difficult to understand or need explanations of the made choices, e.g. even for moderately complex algorithms (like a sorting algorithm), due to an existence of edge-cases, or performance optimizations. This means documenting `What` in addition to `Why` is sometimes admissible. You MUST assume the reader of the code has a less than average experienced when making the decisions whether to add a comment or not.

- The commands in the documentation MUST be executable, ready to be copied by the user. DO NOT write incomplete commands, like `Change directory to tests, then run `echo tests`, but instead write `cd tests && echo tests`.

- You MUST obey the principle of least astonishment. Every method MUST do the least surprising thing it could, given its name. If a method does NOT do what users think it will, bugs will result.

- You MUST use consistent parameter ordering across methods. Otherwise, programmers will get it backwards.

- Design is an art, NOT a science. Strive for beauty, and trust your gut. Do NOT adhere slavishly to the above heuristics, but violate them ONLY infrequently and with good reason.

# python usage

You MUST ALWAYS use type annotations.
You MUST NOT duplicate the type in the docstring.

You MUST AVOID third-party dependencies if possible.

You MUST prefer explicit over implicit.
You MUST AVOID magic behavior.
You MUST be clear in intent, even if it takes a couple of extra lines.

You MUST NOT delete existing tests, unless requested.

You MUST sort requirements.txt.
