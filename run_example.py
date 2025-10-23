#!/usr/bin/env python3
"""
Script de exemplo para execução rápida do sistema multi-agent.
"""
import asyncio
import subprocess
import sys
from pathlib import Path


async def check_redis():
    """Verifica se Redis está disponível."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis está rodando")
        return True
    except Exception as e:
        print(f"✗ Redis não disponível: {e}")
        print("  Para iniciar Redis: docker run -d -p 6379:6379 redis:alpine")
        return False


def check_dependencies():
    """Verifica dependências instaladas."""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'pydantic-settings', 
        'httpx', 'loguru', 'redis'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"✗ {package} não encontrado")
    
    if missing:
        print(f"\nPara instalar dependências faltando:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True


def setup_environment():
    """Configura ambiente se necessário."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print("Copiando .env.example para .env...")
        env_file.write_text(env_example.read_text())
        print("✓ Arquivo .env criado")
        print("  Configure suas chaves de API no arquivo .env")
    
    # Cria diretório de logs
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✓ Diretório de logs criado")


async def main():
    """Função principal."""
    print("\ud83e\udd16 Multi-Agent System - Exemplo de Execução")
    print("=" * 50)
    
    print("\n1. Verificando dependências...")
    if not check_dependencies():
        print("\n✗ Instale as dependências primeiro: pip install -r requirements.txt")
        return
    
    print("\n2. Verificando Redis...")
    redis_ok = await check_redis()
    
    print("\n3. Configurando ambiente...")
    setup_environment()
    
    if not redis_ok:
        print("\n⚠️  Aviso: Redis não está disponível")
        print("   O sistema irá funcionar com funcionalidades limitadas")
    
    print("\n4. Iniciando sistema...")
    print("-" * 30)
    
    try:
        # Adiciona src ao PYTHONPATH
        import sys
        from pathlib import Path
        src_path = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_path))
        
        # Importa e inicia o sistema
        from main import main as run_system
        await run_system()
        
    except KeyboardInterrupt:
        print("\n\nℹ️ Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n✗ Erro ao iniciar sistema: {e}")
        print("\nPara mais detalhes, verifique os logs em: logs/multi-agent.log")


if __name__ == "__main__":
    asyncio.run(main())