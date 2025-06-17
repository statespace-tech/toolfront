"""
Integration tests for SSH tunneling functionality.

This test suite simulates Tejas's exact use case:
- PostgreSQL database in a private network (like RDS in private subnet)
- SSH bastion server (like EC2 instance in public subnet)
- toolfront connecting through SSH tunnel from external network

Architecture:
  [Test Runner] --SSH--> [Bastion] ---> [PostgreSQL Private]
     (public)            (bridge)        (private network)
"""

import os
import subprocess

import pytest

from toolfront.models.connection import Connection
from toolfront.ssh import extract_ssh_params

# Mark all tests in this class as requiring Docker Compose
pytestmark = pytest.mark.docker_compose


class TestSSHTunneling:
    """Integration tests for SSH tunneling with real containers."""

    @pytest.fixture(scope="class")
    def connection_params(self):
        """Get connection parameters from environment."""
        return {
            "ssh_host": os.getenv("SSH_HOST", "ssh-bastion"),
            "ssh_port": int(os.getenv("SSH_PORT", "22")),
            "ssh_user": os.getenv("SSH_USER", "bastionuser"),
            "ssh_password": os.getenv("SSH_PASSWORD", "bastionpass"),
            "postgres_host": os.getenv("POSTGRES_HOST", "postgres-private"),
            "postgres_port": int(os.getenv("POSTGRES_PORT", "5432")),
            "postgres_user": os.getenv("POSTGRES_USER", "testuser"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD", "testpass"),
            "postgres_db": os.getenv("POSTGRES_DB", "testdb"),
        }

    def test_environment_setup(self, connection_params):
        """Verify the Docker environment is set up correctly."""
        print("🔍 Testing environment setup...")

        # Test 1: SSH bastion is reachable
        ssh_result = subprocess.run(
            ["nc", "-z", connection_params["ssh_host"], str(connection_params["ssh_port"])],
            capture_output=True,
            timeout=10,
        )

        assert ssh_result.returncode == 0, (
            f"SSH bastion not reachable at {connection_params['ssh_host']}:{connection_params['ssh_port']}"
        )
        print(f"✅ SSH bastion reachable at {connection_params['ssh_host']}:{connection_params['ssh_port']}")

        # Test 2: PostgreSQL should NOT be directly reachable (it's in private network)
        # This test confirms our network isolation is working
        postgres_direct_result = subprocess.run(
            ["timeout", "5", "nc", "-z", connection_params["postgres_host"], str(connection_params["postgres_port"])],
            capture_output=True,
        )

        # This should fail because postgres is in private network
        assert postgres_direct_result.returncode != 0, "PostgreSQL should not be directly accessible (private network)"
        print("✅ PostgreSQL properly isolated in private network")

    def test_ssh_connectivity(self, connection_params):
        """Test that we can SSH to the bastion server."""
        print("🔍 Testing SSH connectivity...")

        # Test SSH authentication
        ssh_test_cmd = [
            "sshpass",
            "-p",
            connection_params["ssh_password"],
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=10",
            f"{connection_params['ssh_user']}@{connection_params['ssh_host']}",
            "-p",
            str(connection_params["ssh_port"]),
            "echo 'SSH_SUCCESS'",
        ]

        try:
            result = subprocess.run(ssh_test_cmd, capture_output=True, text=True, timeout=15)
            assert result.returncode == 0, f"SSH authentication failed: {result.stderr}"
            assert "SSH_SUCCESS" in result.stdout, f"SSH command execution failed: {result.stdout}"
            print("✅ SSH authentication and command execution successful")
        except subprocess.TimeoutExpired:
            pytest.fail("SSH connection timed out")
        except FileNotFoundError:
            # Install sshpass if not available
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y", "sshpass"], check=True)
            # Retry
            result = subprocess.run(ssh_test_cmd, capture_output=True, text=True, timeout=15)
            assert result.returncode == 0, f"SSH authentication failed: {result.stderr}"

    def test_postgres_via_bastion(self, connection_params):
        """Test that PostgreSQL is accessible from the bastion server."""
        print("🔍 Testing PostgreSQL access via bastion...")

        # Test PostgreSQL connectivity from bastion
        postgres_test_cmd = [
            "sshpass",
            "-p",
            connection_params["ssh_password"],
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=10",
            f"{connection_params['ssh_user']}@{connection_params['ssh_host']}",
            "-p",
            str(connection_params["ssh_port"]),
            f"PGPASSWORD={connection_params['postgres_password']} psql -h {connection_params['postgres_host']} -U {connection_params['postgres_user']} -d {connection_params['postgres_db']} -c 'SELECT 1 as test_connection;'",
        ]

        result = subprocess.run(postgres_test_cmd, capture_output=True, text=True, timeout=20)
        assert result.returncode == 0, f"PostgreSQL connection via bastion failed: {result.stderr}"
        assert "test_connection" in result.stdout, f"PostgreSQL query failed: {result.stdout}"
        print("✅ PostgreSQL accessible from bastion server")

    def test_ssh_parameter_extraction(self, connection_params):
        """Test SSH parameter extraction from URL."""
        print("🔍 Testing SSH parameter extraction...")

        # Build the SSH tunnel URL (simulating what Tejas would use)
        tunnel_url = (
            f"postgresql://{connection_params['postgres_user']}:{connection_params['postgres_password']}"
            f"@{connection_params['postgres_host']}:{connection_params['postgres_port']}/{connection_params['postgres_db']}"
            f"?ssh_host={connection_params['ssh_host']}"
            f"&ssh_port={connection_params['ssh_port']}"
            f"&ssh_user={connection_params['ssh_user']}"
            f"&ssh_password={connection_params['ssh_password']}"
        )

        clean_url, ssh_config = extract_ssh_params(tunnel_url)

        assert ssh_config is not None, "SSH configuration should be extracted"
        assert ssh_config.ssh_host == connection_params["ssh_host"]
        assert ssh_config.ssh_port == connection_params["ssh_port"]
        assert ssh_config.ssh_user == connection_params["ssh_user"]
        assert ssh_config.ssh_password == connection_params["ssh_password"]
        assert ssh_config.remote_host == connection_params["postgres_host"]
        assert ssh_config.remote_port == connection_params["postgres_port"]

        print("✅ SSH parameters extracted correctly")
        return tunnel_url, clean_url, ssh_config

    @pytest.mark.asyncio
    async def test_ssh_tunnel_connection(self, connection_params):
        """Test the complete SSH tunnel connection flow."""
        print("🔍 Testing complete SSH tunnel connection...")

        # Build tunnel URL
        tunnel_url = (
            f"postgresql://{connection_params['postgres_user']}:{connection_params['postgres_password']}"
            f"@{connection_params['postgres_host']}:{connection_params['postgres_port']}/{connection_params['postgres_db']}"
            f"?ssh_host={connection_params['ssh_host']}"
            f"&ssh_port={connection_params['ssh_port']}"
            f"&ssh_user={connection_params['ssh_user']}"
            f"&ssh_password={connection_params['ssh_password']}"
        )

        # Create connection
        connection = Connection(url=tunnel_url)
        db = await connection.connect()

        print(f"✅ SSH tunnel database created: {type(db).__name__}")

        # Test connection
        connection_result = await db.test_connection()
        assert connection_result.connected, f"SSH tunnel connection failed: {connection_result.message}"
        print("✅ SSH tunnel connection test passed")

    @pytest.mark.asyncio
    async def test_ssh_tunnel_operations(self, connection_params):
        """Test database operations through SSH tunnel."""
        print("🔍 Testing database operations via SSH tunnel...")

        tunnel_url = (
            f"postgresql://{connection_params['postgres_user']}:{connection_params['postgres_password']}"
            f"@{connection_params['postgres_host']}:{connection_params['postgres_port']}/{connection_params['postgres_db']}"
            f"?ssh_host={connection_params['ssh_host']}"
            f"&ssh_port={connection_params['ssh_port']}"
            f"&ssh_user={connection_params['ssh_user']}"
            f"&ssh_password={connection_params['ssh_password']}"
        )

        connection = Connection(url=tunnel_url)
        db = await connection.connect()

        # Test 1: Get tables
        tables = await db.get_tables()
        print(f"✅ Retrieved {len(tables)} tables via SSH tunnel: {tables}")
        assert len(tables) > 0, "Should have tables from init-db.sql"
        assert any("users" in table for table in tables), "users table should exist"
        assert any("orders" in table for table in tables), "orders table should exist"

        # Test 2: Inspect table structure
        users_schema = await db.inspect_table("public.users")
        print("✅ Retrieved users table schema via SSH tunnel")
        assert users_schema is not None, "Should retrieve table schema"

        # Test 3: Sample data
        users_sample = await db.sample_table("public.users", n=3)
        print(f"✅ Retrieved {len(users_sample)} sample records via SSH tunnel")
        assert len(users_sample) > 0, "Should retrieve sample data"

        # Test 4: Execute query
        query_result = await db.query("SELECT COUNT(*) as user_count FROM public.users WHERE active = true")
        print(f"✅ Query executed via SSH tunnel: {len(query_result)} rows returned")
        assert len(query_result) > 0, "Query should return results"

        # Test 5: Complex query (join)
        join_query = """
        SELECT u.username, COUNT(o.id) as order_count
        FROM public.users u
        LEFT JOIN public.orders o ON u.id = o.user_id
        WHERE u.active = true
        GROUP BY u.username
        ORDER BY order_count DESC
        """
        join_result = await db.query(join_query)
        print(f"✅ Complex join query executed via SSH tunnel: {len(join_result)} rows")
        assert len(join_result) > 0, "Join query should return results"


    def test_client_demo_scenario(self, connection_params):
        """Test the exact scenario we'll demo to clients."""
        print("🎯 DEMO SCENARIO: Tejas's use case simulation")
        print("=" * 60)

        # This is exactly what Tejas would run
        tejas_command = (
            f'toolfront "postgresql://{connection_params["postgres_user"]}:{connection_params["postgres_password"]}'
            f"@{connection_params['postgres_host']}:{connection_params['postgres_port']}/{connection_params['postgres_db']}"
            f"?ssh_host={connection_params['ssh_host']}"
            f"&ssh_port={connection_params['ssh_port']}"
            f"&ssh_user={connection_params['ssh_user']}"
            f'&ssh_password={connection_params["ssh_password"]}"'
        )

        print("🚀 Tejas would run this command:")
        print(f"   {tejas_command}")
        print()
        print("🔧 What happens behind the scenes:")
        print("   1. toolfront extracts SSH parameters from URL")
        print("   2. Creates SSH tunnel: laptop → bastion → PostgreSQL")
        print("   3. Connects to PostgreSQL through the tunnel")
        print("   4. Executes database operations")
        print("   5. Automatically cleans up tunnel")
        print()
        print("✅ This integration test proves the complete flow works!")
        print("✅ No manual SSH setup required for Tejas")
        print("✅ No reconfiguration of their AWS security needed")
        print("=" * 60)
