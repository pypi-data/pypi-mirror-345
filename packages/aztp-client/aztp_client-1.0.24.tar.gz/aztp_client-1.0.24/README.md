# AZTP Client Python

AZTP (Agentic Zero Trust Protocol) Client is an enterprise-grade identity service client that provides secure workload identity management using AZTP standards. The client library facilitates secure communication between workloads by managing digital identities and certificates.

## Installation

```bash
pip install aztp-client
```

## Requirements

- Python 3.8 or higher

## Trusted Domains

The AZTP client maintains a whitelist of trusted domains for use with the `trustDomain` parameter. When you specify a domain that isn't in this whitelist, the client will display a warning and suggest valid alternatives from the approved list. If no trust domain is specified, the system defaults to `aztp.network`.

```python
from aztp_client import Aztp, whiteListTrustDomains

# Check available trusted domains
print("Available trusted domains:", whiteListTrustDomains)

# Create a secure connection with a trusted domain
agent = await client.secure_connect(
    crew_agent={},
    "my-agent",
    config={
        "trustDomain": whiteListTrustDomains["gptapps.ai"],  # Using a whitelisted domain
        "isGlobalIdentity": False
    }
)
```

### Current Trusted Domains

- `gptarticles.xyz`
- `gptapps.ai`
- `vcagents.ai`

## Quick Start

```python
from aztp_client import Aztp, whiteListTrustDomains

# Initialize client
client = Aztp(api_key="your-api-key")

# Create a secure agent
agent = await client.secure_connect(
    crew_agent={},
    "service1",
    config={
        "isGlobalIdentity": False
    }
)

# Create a secure agent with a trusted domain
agent_with_domain = await client.secure_connect(
    crew_agent={},
    'service2',
    config={
        "trustDomain": whiteListTrustDomains["gptapps.ai"],  # Using first whitelisted domain
        "isGlobalIdentity": False
    }
)

# Verify identity
is_valid = await client.verify_identity(agent)

# Verify the identity connection
is_valid_connection = await client.verify_identity_connection(from_aztp_id, to_aztp_id)

# Get identity access policy
# Returns the access policy for the specified AZTP identity
# Raises ValueError if aztp_id is not properly formatted
# Raises RequestException if the request fails
identity_policy = await client.get_policy(agent.identity.aztp_id)

# Check available trusted domains
print("Available trusted domains:", whiteListTrustDomains)

# Get identity details
identity = await client.get_identity(agent)

# Discover identities
discovered_identities = await client.discover_identity()

# Discover identities with trust domain and requestor identity
discovered_identities = await client.discover_identity(trust_domain, requestor_identity)

# Revoke an identity
revoke_result = await client.revoke_identity(
    aztp_id=agent.identity.aztp_id,
    reason="Identity no longer needed"  # Optional reason
)

# Undo a revoked identity
undo_result = await client.undo_revoke_identity(agent.identity.aztp_id)
```

## Core Methods

### Identity Management

- `secure_connect(crew_agent, name, config)`: Create a secure connection for a workload
- `verify_identity(agent)`: Verify the identity of a secured agent
- `verify_identity_connection(from_aztp_id, to_aztp_id)`: Verify connection between two agents
- `get_identity(agent)`: Get identity information for a secured agent
- `discover_identity(trust_domain, requestor_identity)`: Discover identities based on parameters
- `revoke_identity(aztp_id, reason)`: Revoke an AZTP identity
  - Parameters:
    - `aztp_id`: Full AZTP ID (e.g., "aztp://domain/workload/environment/method/name")
    - `reason`: Optional reason for revocation
  - Returns: JSON-formatted revocation result
  - Raises:
    - `ValueError`: If aztp_id is not properly formatted
    - `RequestException`: If the request fails
- `undo_revoke_identity(aztp_id)`: Restore a previously revoked identity
  - Parameters:
    - `aztp_id`: Full AZTP ID (e.g., "aztp://domain/workload/environment/method/name")
  - Returns: JSON-formatted restoration result
  - Raises:
    - `ValueError`: If aztp_id is not properly formatted
    - `RequestException`: If the request fails

### Policy Management

- `get_policy(aztp_id)`: Get access policy for a specific AZTP identity
  - Parameters:
    - `aztp_id`: Full AZTP ID (e.g., "aztp://domain/workload/environment/method/name")
  - Returns: JSON-formatted access policy information
  - Raises:
    - `ValueError`: If aztp_id is not properly formatted
    - `RequestException`: If the request fails

## Example

```python
import asyncio
import os
from pathlib import Path
from aztp_client import Aztp
from dotenv import load_dotenv

# Load the .env file from the correct location
load_dotenv()

async def main():
    # Initialize the client with your API key
    client = Aztp(
        api_key= os.getenv("AZTP_API_KEY")
    )
    name = os.getenv("AZTP_AGENT_NAME")
    otherNameA = os.getenv("AZTP_OTHER_AGENT_NAME_A")
    otherNameB = os.getenv("AZTP_OTHER_AGENT_NAME_B")

    # Get trust domain from environment or use a whitelisted domain
    from aztp_client import whiteListTrustDomains
    trustDomain = os.getenv("AZTP_TRUST_DOMAIN") or whiteListTrustDomains["gptapps.ai"]

    # Validate trust domain against whitelist
    if trustDomain not in whiteListTrustDomains:
        print(f"Warning: Trust domain '{trustDomain}' is not in the whitelist.")
        print(f"Available trusted domains: {', '.join(whiteListTrustDomains)}")
        trustDomain = 'aztp.network'

    try:
        crewAgent = {}
        crewAgentA = {}
        crewAgentB = {}

        # Create a secure agent
        print("\nCreating secure agent...")
        agent = await client.secure_connect(
            crewAgent,
            name,
            {
                "isGlobalIdentity": True
            }
        )
        print(f"Agent {name} created successfully!")

        if agent.identity.aztp_id:
            print(f"Agent: {agent.identity.aztp_id}")

        # Get and display the identity access policy
        print("\nRetrieving identity access policy...")
        try:
            identity_policy = await client.get_policy(agent.identity.aztp_id)
            print("\nIdentity access policy:", identity_policy)

            # Process and display policy statements
            for policy in identity_policy.data:
                print("\nPolicy Statement:", policy.policyStatement)
                if policy.policyStatement.Statement[0].Effect == "Allow":
                    print("Statement Effect:", policy.policyStatement.Statement[0].Effect)
                    print("Statement Actions:", policy.policyStatement.Statement[0].Action)
                    if hasattr(policy.policyStatement.Statement[0], 'Condition'):
                        print("Statement Conditions:", policy.policyStatement.Statement[0].Condition)
                    print("Identity:", policy.identity)
        except ValueError as e:
            print(f"Invalid AZTP ID format: {e}")
        except Exception as e:
            print(f"Failed to retrieve access policy: {e}")

        #Example 1: Create a agent with linked identity
        print("\nCreating agent with linked identity...")
        agentA = await client.secure_connect(
            crewAgentA,
            otherNameA,
            {
                "linkTo": [agent.identity.aztp_id],
                "isGlobalIdentity": False
            }
        )
        print(f"Agent {otherNameA} created successfully!")
        if agentA.identity.aztp_id:
            print(f"Agent: {agentA.identity.aztp_id}")

        #Example 2: Create a agent with linked identity, parent identity and trust domain
        print("\nCreating agent with linked identity and trust domain...")
        agentB = await client.secure_connect(
            crewAgentB,
            otherNameB,
            {
                "linkTo": [agent.identity.aztp_id],
                "parentIdentity": agentA.identity.aztp_id,
                "trustDomain": trustDomain,  # Using validated trust domain from whitelist
                "isGlobalIdentity": False
            }
        )
        print(f"Agent {otherNameB} created successfully!")
        if agentB.identity.aztp_id:
            print(f"Agent: {agentB.identity.aztp_id}")


        # Verify the identity
        print(f"\nVerifying agent {name} identity...")
        is_valid = await client.verify_identity(agent)
        print(f"Identity valid: {is_valid}")

        # Verify the identity connection
        print(f"\nVerifying agent {name} identity connection with {otherNameB}...")
        is_valid_connection = await client.verify_identity_connection(agent.identity.aztp_id, agentB.identity.aztp_id)
        print(f"Connection valid: {is_valid_connection}")

        # Get identity details
        print(f"\nGetting agent {name} identity details...")
        identity = await client.get_identity(agent)
        if identity:
            print(f"Retrieved identity: {identity}")
        else:
            print("No identity found")

        # Discover identities
        print(f"\nDiscovering all identities...")
        discovered_identities = await client.discover_identity()
        print(f"Discovered identities: {discovered_identities}")

        # Discover identities with trust domain and requestor identity
        print(f"\nDiscovering identities with trust domain {trustDomain} and requestor identity {agent.identity.aztp_id}...")
        discovered_identities = await client.discover_identity(trust_domain=trustDomain, requestor_identity=agent.identity.aztp_id)
        print(f"Discovered identities with trust domain and requestor identity: {discovered_identities}")

        # Revoke Identity
        print("\nRevoking identity...")
        revoke_result = await client.revoke_identity(
            aztp_id=agent.identity.aztp_id,
            reason="Service decommissioned"  # Optional reason for revocation
        )
        print(f"Identity revocation result: {revoke_result}")

        # Undo revoke Identity
        print("\nRestoring revoked identity...")
        restore_result = await client.undo_revoke_identity(
            aztp_id=agent.identity.aztp_id
        )
        print(f"Identity restoration result: {restore_result}")

    except ConnectionError as e:
        print(f"Connection Error: Could not connect to the AZTP server. Please check your connection and server URL.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nCurrent configuration:")
        print(f"Base URL: {client.config.base_url}")
        print(f"Environment: {client.config.environment}")
        print("API Key: ********")  # Don't print the API key for security

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Workload Identity Management using AZTP standards
- Certificate Management (X.509)
- Secure Communication
- Identity Verification
- Identity Access Policy Management
- Metadata Management
- Environment-specific Configuration
- Trusted Domain Validation and Suggestions

## Error Handling

The client includes comprehensive error handling for various scenarios:

- **Connection Errors**: Handles network and server connectivity issues
- **Authentication Errors**: Manages API key and authentication failures
- **Validation Errors**: Validates input parameters and trust domains
- **Policy Errors**: Handles policy retrieval and validation failures

## License

MIT License
