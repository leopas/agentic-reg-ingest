#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""
Script para limpar dados da feature Vision Enrichment.

Este script remove:
- Registros da tabela vision_upload
- Arquivos físicos (uploads, JSONL, TXTs)
- Opcionalmente: agentic_plan, search_results, chunk_manifest relacionados
"""

import argparse
import shutil
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.session import DatabaseSession
from db.models import VisionUpload, ChunkManifest
from sqlalchemy import text, select


def get_vision_uploads(session):
    """Get all vision uploads."""
    return list(session.scalars(select(VisionUpload)))


def cleanup_vision_enrichment(
    session,
    dry_run: bool = True,
    delete_files: bool = True,
    delete_agentic_data: bool = False,
    delete_chunks: bool = False,
):
    """
    Clean up vision enrichment data.
    
    Args:
        session: Database session
        dry_run: If True, only show what would be deleted
        delete_files: If True, delete physical files
        delete_agentic_data: If True, delete agentic_plan and search_results
        delete_chunks: If True, delete chunk_manifest entries
    """
    print("=" * 80)
    print("🧹 LIMPEZA: Vision Enrichment")
    print("=" * 80)
    print()
    
    # Get all uploads
    uploads = get_vision_uploads(session)
    
    if not uploads:
        print("✓ Nenhum upload encontrado. Nada para limpar.")
        return
    
    print(f"📊 Uploads encontrados: {len(uploads)}")
    print()
    
    # Show what will be deleted
    files_to_delete = []
    dirs_to_delete = []
    
    for upload in uploads:
        print(f"📄 {upload.original_filename}")
        print(f"   ID: {upload.upload_id}")
        print(f"   Status: {upload.status}")
        print(f"   Criado: {upload.created_at}")
        
        if delete_files:
            # Original file
            if upload.file_path and Path(upload.file_path).exists():
                files_to_delete.append(upload.file_path)
                print(f"   ✗ Arquivo: {upload.file_path}")
            
            # JSONL
            if upload.jsonl_path and Path(upload.jsonl_path).exists():
                files_to_delete.append(upload.jsonl_path)
                print(f"   ✗ JSONL: {upload.jsonl_path}")
            
            # TXT output dir
            if upload.txt_output_dir and Path(upload.txt_output_dir).exists():
                dirs_to_delete.append(upload.txt_output_dir)
                txt_count = len(list(Path(upload.txt_output_dir).glob("*.txt")))
                print(f"   ✗ TXT Dir: {upload.txt_output_dir} ({txt_count} arquivos)")
        
        print()
    
    # Count related data
    plan_ids = [u.plan_id for u in uploads if u.plan_id]
    
    if delete_agentic_data and plan_ids:
        plans_count = session.execute(
            text("SELECT COUNT(*) FROM agentic_plan WHERE plan_id IN :ids"),
            {"ids": tuple(plan_ids)}
        ).scalar()
        
        results_count = session.execute(
            text("SELECT COUNT(*) FROM search_results WHERE plan_id IN :ids"),
            {"ids": tuple(plan_ids)}
        ).scalar()
        
        print(f"📋 Agentic Plans: {plans_count}")
        print(f"🔍 Search Results: {results_count}")
        print()
    
    if delete_chunks:
        upload_ids = [u.upload_id for u in uploads]
        
        # Find chunks that have upload_id in meta
        chunks_count = 0
        try:
            chunks = session.query(ChunkManifest).all()
            for chunk in chunks:
                if chunk.meta:
                    import json
                    meta = json.loads(chunk.meta) if isinstance(chunk.meta, str) else chunk.meta
                    if meta.get("upload_id") in upload_ids or chunk.source_pipeline == "enrichment":
                        chunks_count += 1
        except Exception as e:
            print(f"⚠️ Erro ao contar chunks: {e}")
        
        if chunks_count > 0:
            print(f"📦 Chunks (source_pipeline=enrichment): {chunks_count}")
            print()
    
    # Summary
    print("=" * 80)
    print("📊 RESUMO:")
    print("=" * 80)
    print(f"  Registros vision_upload: {len(uploads)}")
    print(f"  Arquivos físicos: {len(files_to_delete)}")
    print(f"  Diretórios: {len(dirs_to_delete)}")
    
    if delete_agentic_data and plan_ids:
        print(f"  Agentic plans: {plans_count}")
        print(f"  Search results: {results_count}")
    
    if delete_chunks and chunks_count > 0:
        print(f"  Chunk manifests: {chunks_count}")
    
    print()
    
    # Dry run mode
    if dry_run:
        print("⚠️  DRY RUN MODE - Nada será deletado")
        print("    Execute com --execute para aplicar as mudanças")
        return
    
    # Confirm
    print("⚠️  ATENÇÃO: ESTA AÇÃO NÃO PODE SER DESFEITA!")
    print()
    response = input("Digite 'DELETAR' para confirmar: ")
    
    if response != "DELETAR":
        print("❌ Cancelado.")
        return
    
    print()
    print("🗑️  Deletando...")
    print()
    
    # Delete files
    if delete_files:
        for file_path in files_to_delete:
            try:
                Path(file_path).unlink()
                print(f"✓ Deletado: {file_path}")
            except Exception as e:
                print(f"✗ Erro ao deletar {file_path}: {e}")
        
        for dir_path in dirs_to_delete:
            try:
                shutil.rmtree(dir_path)
                print(f"✓ Deletado: {dir_path}/")
            except Exception as e:
                print(f"✗ Erro ao deletar {dir_path}: {e}")
    
    # Delete agentic data
    if delete_agentic_data and plan_ids:
        try:
            session.execute(
                text("DELETE FROM search_results WHERE plan_id IN :ids"),
                {"ids": tuple(plan_ids)}
            )
            print(f"✓ Deletados {results_count} search_results")
            
            session.execute(
                text("DELETE FROM agentic_plan WHERE plan_id IN :ids"),
                {"ids": tuple(plan_ids)}
            )
            print(f"✓ Deletados {plans_count} agentic_plans")
        except Exception as e:
            print(f"✗ Erro ao deletar dados agentic: {e}")
    
    # Delete chunks
    if delete_chunks and chunks_count > 0:
        try:
            # Delete by source_pipeline
            deleted = session.execute(
                text("DELETE FROM chunk_manifest WHERE source_pipeline = 'enrichment'")
            ).rowcount
            print(f"✓ Deletados {deleted} chunk_manifests")
        except Exception as e:
            print(f"✗ Erro ao deletar chunks: {e}")
    
    # Delete vision_upload records
    try:
        for upload in uploads:
            session.delete(upload)
        session.commit()
        print(f"✓ Deletados {len(uploads)} registros vision_upload")
    except Exception as e:
        session.rollback()
        print(f"✗ Erro ao deletar uploads: {e}")
        return
    
    print()
    print("=" * 80)
    print("✅ LIMPEZA CONCLUÍDA!")
    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Limpar dados da feature Vision Enrichment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:

  # Dry run (apenas mostrar o que seria deletado)
  python scripts/cleanup_vision_enrichment.py

  # Deletar apenas vision_upload e arquivos
  python scripts/cleanup_vision_enrichment.py --execute

  # Deletar TUDO (incluindo agentic_plan, search_results, chunks)
  python scripts/cleanup_vision_enrichment.py --execute --all

  # Deletar apenas registros do banco (manter arquivos)
  python scripts/cleanup_vision_enrichment.py --execute --no-files

  # Deletar tudo exceto chunks
  python scripts/cleanup_vision_enrichment.py --execute --agentic-data
        """
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Executar a limpeza (sem isso, apenas mostra o que seria deletado)"
    )
    
    parser.add_argument(
        "--no-files",
        action="store_true",
        help="Não deletar arquivos físicos (apenas registros do banco)"
    )
    
    parser.add_argument(
        "--agentic-data",
        action="store_true",
        help="Deletar também agentic_plan e search_results relacionados"
    )
    
    parser.add_argument(
        "--chunks",
        action="store_true",
        help="Deletar também chunk_manifest com source_pipeline='enrichment'"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Deletar TUDO (equivalente a --agentic-data --chunks)"
    )
    
    args = parser.parse_args()
    
    # Process flags
    delete_files = not args.no_files
    delete_agentic = args.agentic_data or args.all
    delete_chunks = args.chunks or args.all
    dry_run = not args.execute
    
    # Execute
    db = DatabaseSession()
    with next(db.get_session()) as session:
        cleanup_vision_enrichment(
            session,
            dry_run=dry_run,
            delete_files=delete_files,
            delete_agentic_data=delete_agentic,
            delete_chunks=delete_chunks,
        )


if __name__ == "__main__":
    main()

