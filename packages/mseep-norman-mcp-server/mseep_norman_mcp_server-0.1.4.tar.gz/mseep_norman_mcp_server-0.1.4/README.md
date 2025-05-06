# [Norman Finance](http://norman.finance?utm_source=mcp_server) MCP Server

A Model Context Protocol (MCP) server that allows Large Language Models (LLMs) to interact with the basic Norman Finance API implementation. This server provides access to accounting, invoices, companies, clients, taxes, and more through a standardized protocol.

> [!NOTE]
> 
> The Norman Finance MCP Server is currently in Beta. We welcome your feedback and encourage you to report any bugs by opening an issue [here](https://github.com/norman-finance/norman-mcp-server/issues).


<a href="https://glama.ai/mcp/servers/@norman-finance/norman-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@norman-finance/norman-mcp-server/badge" alt="Norman Finance Server MCP server" />
</a>
<br/>

## Features

- 🔐 **Authentication**: Securely authenticate with the Norman Finance API
- 💼 **Company Management**: View and update company details
- 📊 **Accounting**: Access and manage transactions
- 📝 **(e-)Invoicing**: Create, view, send, and manage compliant invoices. For example, create a recurring invoice based on the contract data
- 👥 **Client Management**: Create and manage clients
- 💰 **Taxes**: View tax information and reports, generate official Finanzamt PDF previews and file taxes
- 📄 **Documents**: Upload and manage attachments

### Use Case Examples with Claude Desktop

Here are some examples of how to use Norman Finance MCP with Claude Desktop:

#### 1. Creating Transactions Using Gmail Receipts

<img width="300" alt="cloudflare_receipt_example" src="https://github.com/user-attachments/assets/2380724b-7a79-45a4-93bd-ddc13a175525" />

#### 2. Managing Overdue Invoices

<img width="300" alt="overdue_reminder_1" src="https://github.com/user-attachments/assets/d59ed22a-5e75-46f6-ad82-db2f637cf7a2" />
<img width="300" alt="overdue_reminder_2" src="https://github.com/user-attachments/assets/26cfb8e9-4725-48a9-b413-077dfb5902e7" />

## Prerequisites

Before using this MCP server, you need to:

1. Create an account on [Norman Finance](https://app.norman.finance/sign-up?utm_source=mcp_server) (or [dev.norman.finance](https://dev.norman.finance/sign-up?utm_source=mcp_server) for the sandbox environment)
2. Have your email and password ready for authentication

## Remote MCP Server
Norman now offers a hosted remote MCP server at:

> http://mcp.norman.finance/sse
The remote MCP is recommended because it utilizes OAuth authentication, enabling you to log in directly with your Norman account without the need to create or manage access tokens manually.
> 
## Installation

### Using Claude Desktop with the Norman MCP Server (via PyPI)

To run the Norman Finance MCP server with Claude Desktop, follow these steps:

#### 1. Install uv

Follow the instructions here: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

#### 2. Download and Configure Claude Desktop

1. Download [Claude Desktop](https://claude.ai/download).

2. Launch Claude and navigate to: Settings > Developer > Edit Config.

3. Update your `claude_desktop_config.json` file with the following configuration:

#### Remote MCP
```json
{
  "mcpServers": {
    "norman-mcp-server": {
      "command": "npx",
      "args": ["mcp-remote", "http://mcp.norman.finance/sse"]
    }
  }
}
```
#### Local MCP

```json
{
  "mcpServers": {
    "norman-mcp-server": {
      "command": "<home_path>/.local/bin/uvx",
      "args": [
        "--from",
        "norman-mcp-server@latest",
        "norman-mcp"
      ],
      "env": {
        "NORMAN_EMAIL": "your-email@example.com",
        "NORMAN_PASSWORD": "your-password",
        "NORMAN_ENVIRONMENT": "production"
      }
    }
  }
}
```

### Installing from Source

If you prefer to run the MCP server from source:

```bash
git clone https://github.com/norman-finance/norman-mcp-server.git
cd norman-mcp-server
pip install -e .
```

Then update your claude_desktop_config.json file to point to the Python module directly:

```json
{
  "mcpServers": {
    "norman-mcp-server": {
      "command": "<path_to_your_python>/python",
      "args": ["-m", "norman_mcp"],
      "env": {
        "NORMAN_EMAIL": "your-email@example.com",
        "NORMAN_PASSWORD": "your-password",
        "NORMAN_ENVIRONMENT": "production"
      }
    }
  }
}
```

## Configuration

### Authentication Methods

The Norman MCP server supports two authentication methods:

#### 1. Environment Variables (for stdio transport)

When using the server with Claude Desktop or stdin/stdout communication, provide credentials through environment variables:

```bash
# .env
NORMAN_EMAIL=your-email@example.com
NORMAN_PASSWORD=your-password
NORMAN_ENVIRONMENT=production  # or "sandbox" for the development environment
NORMAN_API_TIMEOUT=200  # Request timeout in seconds
```

#### 2. OAuth Authentication (for SSE transport)

When using the server with MCP Inspector, Claude API, or other SSE clients, the server uses OAuth 2.0 authentication:

1. Start the server with SSE transport:
   ```bash
   python -m norman_mcp --transport sse
   ```

2. When connecting to the server, you'll be directed to a login page
3. Enter your Norman Finance credentials
4. You'll be redirected back to your application with authentication tokens

### Environment Variables

The server can be configured using these environment variables:

```bash
# Authentication (for stdio transport)
NORMAN_EMAIL=your-email@example.com
NORMAN_PASSWORD=your-password
NORMAN_ENVIRONMENT=production  # or "sandbox" for the development environment

# Server configuration
NORMAN_MCP_HOST=0.0.0.0  # Host to bind to
NORMAN_MCP_PORT=3001     # Port to bind to
NORMAN_MCP_PUBLIC_URL=http://example.com  # Public URL for OAuth callbacks (important for remote access)
NORMAN_API_TIMEOUT=200   # Request timeout in seconds
```

### Command Line Arguments

Alternatively, you can provide the credentials through command line arguments:

```bash
norman-mcp --email your-email@example.com --password your-password --environment production
```

## Usage

### With Claude or Other MCP-Compatible LLMs

1. Start the MCP server using one of these methods:

   ```bash
   # For stdio transport (environment variable authentication)
   python -m norman_mcp --transport stdio
   
   # For SSE transport (OAuth authentication)
   python -m norman_mcp --transport sse
   ```

2. Connect to the server using your preferred MCP client.

### Helper Scripts

The package includes helper scripts for different use cases:

```bash
# Run with stdio transport (environment variable authentication)
./tools/run_stdio.sh

# Run with remote access using ngrok (for sharing with others)
./tools/run_remote.sh
```

### Integration with Claude Desktop

You can install the server using the MCP CLI:

```bash
mcp install norman-mcp
```

Configure your Norman Finance credentials when prompted.

### Direct Execution

You can also run the server directly with:

```bash
python -m norman_mcp
```

## Resources

This MCP server exposes the following resources:

- `company://current` - Details about your current company
- `transactions://list/{page}/{page_size}` - List of transactions with pagination
- `invoices://list/{page}/{page_size}` - List of invoices with pagination
- `clients://list/{page}/{page_size}` - List of clients with pagination
- `taxes://list/{page}/{page_size}` - List of tax reports with pagination
- `categories://list` - List of transaction categories

## Tools

The MCP server provides the following tools for Norman Finance API interaction:

### Company Management

- `get_company_details()` - Get detailed information about your company
- `update_company_details(name, profession, address, etc.)` - Update company information
- `get_company_balance()` - Get the current balance of the company
- `get_company_tax_statistics()` - Get tax statistics for the company
- `get_vat_next_report()` - Get the VAT amount for the next report period

### Transaction Management

- `search_transactions(description, from_date, to_date, min_amount, max_amount, etc.)` - Search for transactions matching criteria
- `create_transaction(amount, description, cashflow_type, etc.)` - Create a new transaction
- `update_transaction(transaction_id, amount, description, etc.)` - Update an existing transaction
- `categorize_transaction(transaction_amount, transaction_description, transaction_type)` - Detect category for a transaction using AI

### Invoice Management

- `create_invoice(client_id, items, etc.)` - Create a new invoice
- `create_recurring_invoice(client_id, items, etc.)` - Create a new recurring invoice
- `get_invoice(invoice_id)` - Get details about a specific invoice
- `send_invoice(invoice_id, subject, body, etc.)` - Send an invoice via email
- `link_transaction(invoice_id, transaction_id)` - Link a transaction to an invoice
- `get_einvoice_xml(invoice_id)` - Get the e-invoice XML for a specific invoice
- `list_invoices(status, from_date, to_date, etc.)` - List invoices with optional filtering

### Client Management

- `list_clients()` - Get a list of all clients
- `get_client(client_id)` - Get detailed information about a specific client
- `create_client(name, client_type, address, etc.)` - Create a new client
- `update_client(client_id, name, client_type, etc.)` - Update an existing client
- `delete_client(client_id)` - Delete a client

### Document Management

- `upload_bulk_attachments(file_paths, cashflow_type)` - Upload multiple file attachments in bulk
- `list_attachments(file_name, linked, attachment_type, etc.)` - Get list of attachments with optional filters
- `create_attachment(file_path, transactions, attachment_type, etc.)` - Create a new attachment
- `link_attachment_transaction(attachment_id, transaction_id)` - Link a transaction to an attachment

### Tax Management

- `list_tax_reports()` - List all available tax reports
- `get_tax_report(report_id)` - Retrieve a specific tax report
- `validate_tax_number(tax_number, region_code)` - Validate a tax number for a specific region
- `generate_finanzamt_preview(report_id)` - Generate a test Finanzamt preview for a tax report
- `submit_tax_report(report_id)` - Submit a tax report to the Finanzamt
- `list_tax_states()` - Get list of available tax states
- `list_tax_settings()` - Get list of tax settings for the current company
- `update_tax_setting(setting_id, tax_type, vat_type, etc.)` - Update a tax setting

## Prompts

The MCP server offers these guided prompts to help users interact with Norman Finance:

- `create_transaction_prompt(amount, description, cashflow_type)` - Create a prompt for adding a new transaction
- `create_client_prompt(name, client_type)` - Create a prompt for adding a new client
- `send_invoice_prompt(invoice_id)` - Create a prompt for sending an invoice via email
- `search_transactions_prompt(date_range)` - Create a prompt for searching transactions

## Example Interactions

Here are some example interactions with the Norman Finance MCP server:

### View Company Details

```
You can view your company details by accessing the company resource.
[LLM accesses company://current]
```

### List Transactions

```
To see your recent financial transactions:
[LLM accesses transactions://list/1/10]
```

### Create a Transaction

```
To create a new expense transaction:
[LLM calls create_transaction with amount=-129.99, description="Office supplies", cashflow_type="EXPENSE"]
```

### Create an Invoice

```
To create a new invoice, I'll use the create_invoice tool.
[LLM calls create_invoice with client_id, items, etc.]
```

## Development

This section is for contributors who want to develop or extend the Norman Finance MCP server.

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/norman-finance/norman-mcp-server.git
   cd norman-mcp-server
   ```

2. Create and activate a virtual environment:
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Or using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   # Using pip
   pip install -e ".[dev]"
   
   # Or using uv
   uv pip install -e ".[dev]"
   ```

4. Create a `.env` file with your Norman Finance credentials:
   ```bash
   cp .env.template .env
   # Edit .env with your credentials
   ```

### Running in Development Mode

To run the MCP server in development mode with the MCP Inspector:

```bash
mcp dev norman_mcp/server.py
```

This will start the server and open the MCP Inspector in your browser, allowing you to test resources and tools interactively.
