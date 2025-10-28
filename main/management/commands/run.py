from django.core.management.base import BaseCommand
from django.db import connection, transaction
from pathlib import Path
import sqlparse

def clean_sql_content(sql_content):
    """
    Cleans SQL content by removing ASCII art comments.
    """
    lines = sql_content.split('\n')
    cleaned_lines = []
    skip_ascii = False

    for line in lines:
        # Skip ASCII art comment blocks
        if '/*' in line and '██' in line:
            skip_ascii = True
            continue
        if skip_ascii and '*/' in line:
            skip_ascii = False
            continue
        if not skip_ascii:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def split_statements(cleaned_sql):
    """
    Splits the cleaned SQL into individual executable statements.
    """
    return [str(stmt).strip() for stmt in sqlparse.parse(cleaned_sql) if stmt]

class Command(BaseCommand):
    help = "Executes SQL files located in the 'sql' directory."

    def handle(self, *args, **options):
        # Get the path to the SQL files directory (next to management commands)
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.stdout.write(self.style.SUCCESS(f'Base directory: {base_dir}'))

        sql_dir = base_dir / 'sql'
        if not sql_dir.exists() or not sql_dir.is_dir():
            self.stdout.write(self.style.ERROR(f"Directory '{sql_dir}' does not exist."))
            return

        sql_files = sorted(sql_dir.glob('*.sql'))
        if not sql_files:
            self.stdout.write(self.style.WARNING(f"No SQL files found in directory '{sql_dir}'."))
            return

        with connection.cursor() as cursor:
            for sql_file in sql_files:
                try:
                    self.stdout.write(self.style.SUCCESS(f"Processing file: {sql_file.name}"))
                    sql_content = sql_file.read_text(encoding='utf-8')
                    cleaned_sql = clean_sql_content(sql_content)
                    statements = split_statements(cleaned_sql)

                    # Use transaction.atomic() for transactional safety
                    with transaction.atomic():
                        for statement in statements:
                            if statement.strip():
                                cursor.execute(statement)
                                self.stdout.write(self.style.SUCCESS(f"Executed statement from {sql_file.name}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error processing {sql_file.name}: {e}"))
                    raise e