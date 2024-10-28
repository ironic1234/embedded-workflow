# Embedded Workflow
## Development
### Neovim
#### LSP - Competions and diagnostics - clangd:
- Configure using Mason, LSPConfig, LuaSnip and nvim-cmp (Lazy configs):
``` lua
-- Mason setup 
{
    "williamboman/mason.nvim",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
        require("mason").setup()
    end,
},

-- Mason LSP Config setup
{
    "williamboman/mason-lspconfig.nvim",
    dependencies = { "williamboman/mason.nvim" },
    event = { "BufReadPre", "BufNewFile" },
    config = function()
        require("mason-lspconfig").setup({
            ensure_installed = { "clangd" },
        })
    end,
},

-- LSP configuration
{
    "neovim/nvim-lspconfig",
    dependencies = { "williamboman/mason-lspconfig.nvim" },
    event = { "BufReadPre", "BufNewFile" },
    config = function()
        local lspconfig = require("lspconfig")
        local servers = { "clangd" }

        local on_attach = function()
            vim.keymap.set("n", "gd", function()
                vim.lsp.buf.definition()
            end)
            vim.keymap.set("n", "gi", function()
                vim.lsp.buf.implementation()
            end)
            vim.keymap.set("n", "gh", function()
                vim.lsp.buf.hover()
            end)
            vim.keymap.set("n", "gD", function()
                vim.diagnostic.open_float()
            end)
            vim.keymap.set("n", "gr", function()
                vim.lsp.buf.references()
            end)
            vim.keymap.set("n", "ga", function()
                vim.lsp.buf.code_action()
            end)
        end

        -- Specify how the border looks like
        local border = {
            { "┌", "FloatBorder" },
            { "─", "FloatBorder" },
            { "┐", "FloatBorder" },
            { "│", "FloatBorder" },
            { "┘", "FloatBorder" },
            { "─", "FloatBorder" },
            { "└", "FloatBorder" },
            { "│", "FloatBorder" },
        }

        -- Add the border on hover and on signature help popup window
        local handlers = {
            ["textDocument/hover"] = vim.lsp.with(vim.lsp.handlers.hover, { border = border }),
            ["textDocument/signatureHelp"] = vim.lsp.with(vim.lsp.handlers.signature_help, { border = border }),
        }

        -- Add border to the diagnostic popup window
        vim.diagnostic.config({
            virtual_text = {
                prefix = "■ ", -- Could be '●', '▎', 'x', '■', , 
            },
            float = {
                border = border,
            },
        })

        for _, server in ipairs(servers) do
            lspconfig[server].setup({
                on_attach = on_attach,
                handlers = handlers,
            })
        end
    end,
},


-- Completion plugins
{
    "hrsh7th/nvim-cmp",
    dependencies = {
        "hrsh7th/cmp-nvim-lsp",
        "hrsh7th/cmp-buffer",
        "hrsh7th/cmp-path",
        "hrsh7th/cmp-cmdline",
        "saadparwaiz1/cmp_luasnip",
        "L3MON4D3/LuaSnip",
    },
    event = { "BufReadPre", "BufNewFile" },
    config = function()
        local cmp_autopairs = require("nvim-autopairs.completion.cmp")
        local cmp = require("cmp")
        cmp.event:on("confirm_done", cmp_autopairs.on_confirm_done())
        cmp.setup({
            snippet = {
                expand = function(args)
                    require("luasnip").lsp_expand(args.body)
                end,
            },
            mapping = {
                ["<C-b>"] = cmp.mapping(cmp.mapping.scroll_docs(-4), { "i", "c" }),
                ["<C-f>"] = cmp.mapping(cmp.mapping.scroll_docs(4), { "i", "c" }),
                ["<C-Space>"] = cmp.mapping(cmp.mapping.complete(), { "i", "c" }),
                ["<C-e>"] = cmp.mapping({
                    i = cmp.mapping.abort(),
                    c = cmp.mapping.close(),
                }),
                ["<CR>"] = cmp.mapping.confirm({ select = true }),
                ["<Tab>"] = cmp.mapping(function(fallback)
                    if cmp.visible() then
                        cmp.select_next_item()
                    elseif require("luasnip").expand_or_jumpable() then
                        require("luasnip").expand_or_jump()
                    else
                        fallback()
                    end
                end, { "i", "s" }),
                ["<S-Tab>"] = cmp.mapping(function(fallback)
                    if cmp.visible() then
                        cmp.select_prev_item()
                    elseif require("luasnip").jumpable(-1) then
                        require("luasnip").jump(-1)
                    else
                        fallback()
                    end
                end, { "i", "s" }),
            },
            window = {
                completion = cmp.config.window.bordered(),
                documentation = cmp.config.window.bordered(),
            },
            sources = cmp.config.sources({
                { name = "nvim_lsp" },
                { name = "luasnip" }, 
                { name = "buffer" },
            }),
        })
    end,
},

-- LuaSnip setup
{
    "L3MON4D3/LuaSnip",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
        require("luasnip.loaders.from_vscode").lazy_load()
    end,
    dependencies = { "rafamadriz/friendly-snippets" },
},
```
 - In the root of each project, you will need a compile_commands.json so that clangd will know how you make your project. You should use compiledb to do this:
``` bash
compiledb <your-compile-command-here>
```
- clangd might give you some errors about not finding include files or some weird unknown flag errors. We can stop these by making a .clangd file:
``` clangd
CompileFlags:
  Remove:
    -mthumb-interwork 
  Add:
    -I/Applications/ArmGNUToolchain/13.3.rel1/arm-none-eabi/arm-none-eabi/include
```
You may have different unknown flags, and your include path may be different for Windows or Linux

#### Formatting - Conform:
- Similarly, configure with Mason, Conform, and Mason-Conform:
``` lua
-- Mason Conform setup
{
    "zapling/mason-conform.nvim",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
        require("mason-conform").setup({
            ensure_installed = { "clang-format" },
        })
    end,
},
-- Auto-format and user command setup
{
    "stevearc/conform.nvim",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
        require("conform").setup({
            formatters_by_ft = {
                c = { "clang-format" },
            },
        })
        -- Format command
        vim.api.nvim_create_user_command("Format", function(args)
            local range = nil
            if args.count ~= -1 then
                local end_line = vim.api.nvim_buf_get_lines(0, args.line2 - 1, args.line2, true)[1]
                range = {
                    start = { args.line1, 0 },
                    ["end"] = { args.line2, end_line:len() },
                }
            end
            require("conform").format({ async = true, lsp_fallback = true, range = range })
            vim.lsp.buf.format()
        end, { range = true })

        -- Auto-format on save
        vim.api.nvim_create_autocmd("BufWritePre", {
            pattern = "*",
            callback = function(args)
                require("conform").format({ bufnr = args.buf })
                vim.lsp.buf.format()
            end,
        })
    end,
},
```
- You will need a .clang-format file to define what kind of C style you are going to use and any other formatting choices. For example, this is the style of formatting used by the Purdue Robomasters Club.
``` yaml
BasedOnStyle: LLVM
IndentWidth: 4
UseTab: Never
ColumnLimit: 0
BreakBeforeBraces: Allman
AllowShortBlocksOnASingleLine: Empty
AllowShortCaseLabelsOnASingleLine: true  # Allows short case labels on a single line
AllowShortFunctionsOnASingleLine: Inline
AllowShortIfStatementsOnASingleLine: true  # Allows short if statements on a single line
AllowShortLoopsOnASingleLine: true
SpaceBeforeParens: ControlStatements
SpaceAfterCStyleCast: true
SpacesInParentheses: false
SpacesInAngles: false
SpacesInContainerLiterals: false
SpaceAfterTemplateKeyword: true
SortIncludes: false
IncludeCategories:
  - Regex: '^<.*>'
    Priority: 1
  - Regex: '^\.\./.*'
    Priority: 2
  - Regex: '^\./.*'
    Priority: 3
  - Regex: '.*'
    Priority: 4
CommentPragmas: 'Keep'
AlignConsecutiveDeclarations: false
```

#### Keybinds
- **`gd`**: Go to definition.
  - **Action**: Jumps to the location where the function, variable, or symbol is defined.

- **`gi`**: Go to implementation.
  - **Action**: Jumps to the implementation of the symbol under the cursor.

- **`gh`**: Show hover information.
  - **Action**: Displays a popup with type or documentation info about the symbol under the cursor.

- **`gD`**: Show diagnostics.
  - **Action**: Opens a floating window with diagnostics for the current line, making it easy to identify issues.

- **`gr`**: Show references.
  - **Action**: Lists all references to the symbol under the cursor, useful for tracking where and how it's used.

- **`ga`**: Show code actions.
  - **Action**: Opens a menu with available actions (like quick fixes or refactoring options) based on the context.

#### Example config
There is an example config in `init.lua`
You should probably add some of your own stuff like theme or line numbers
