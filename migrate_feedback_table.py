"""
Script de migração para adicionar colunas user_id e titulo à tabela feedback.
Execute este script apenas uma vez após fazer pull das alterações.

Uso:
    python migrate_feedback_table.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agenciaviagens.settings')
django.setup()

from django.db import connection

def migrate_feedback_table():
    """Adiciona colunas user_id e titulo à tabela feedback e atualiza dados existentes"""
    with connection.cursor() as cursor:
        print("=== Migração da tabela feedback ===\n")
        
        # 1. Adicionar coluna user_id
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='feedback' AND column_name='user_id'
            """)
            
            if cursor.fetchone() is None:
                print("1. Adicionando coluna user_id...")
                cursor.execute("ALTER TABLE feedback ADD COLUMN user_id INTEGER")
                cursor.execute("""
                    ALTER TABLE feedback 
                    ADD CONSTRAINT fk_feedback_user 
                    FOREIGN KEY (user_id) REFERENCES utilizador(user_id)
                """)
                print("   ✓ Coluna user_id adicionada com sucesso")
            else:
                print("1. ✓ Coluna user_id já existe")
        except Exception as e:
            print(f"   ✗ Erro ao adicionar user_id: {e}")
            raise
        
        # 2. Adicionar coluna titulo
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='feedback' AND column_name='titulo'
            """)
            
            if cursor.fetchone() is None:
                print("2. Adicionando coluna titulo...")
                cursor.execute("ALTER TABLE feedback ADD COLUMN titulo VARCHAR(200)")
                print("   ✓ Coluna titulo adicionada com sucesso")
            else:
                print("2. ✓ Coluna titulo já existe")
        except Exception as e:
            print(f"   ✗ Erro ao adicionar titulo: {e}")
            raise
        
        # 3. Atualizar feedbacks existentes com user_id
        try:
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE user_id IS NULL")
            count_null = cursor.fetchone()[0]
            
            if count_null > 0:
                print(f"3. Atualizando {count_null} feedbacks com user_id...")
                cursor.execute("""
                    UPDATE feedback f
                    SET user_id = c.user_id
                    FROM (
                        SELECT DISTINCT ON (pacote_id) pacote_id, user_id
                        FROM compra
                        ORDER BY pacote_id, data_compra
                    ) c
                    WHERE f.pacote_id = c.pacote_id
                    AND f.user_id IS NULL
                """)
                rows_updated = cursor.rowcount
                print(f"   ✓ {rows_updated} feedbacks atualizados")
            else:
                print("3. ✓ Todos os feedbacks já têm user_id")
        except Exception as e:
            print(f"   ✗ Erro ao atualizar feedbacks: {e}")
            raise
        
        print("\n✓ Migração concluída com sucesso!")
        print("\nPodes agora excluir este script se quiseres.")

if __name__ == '__main__':
    try:
        migrate_feedback_table()
    except Exception as e:
        print(f"\n✗ Erro durante a migração: {e}")
        print("Por favor, resolve o erro e executa o script novamente.")
        exit(1)
