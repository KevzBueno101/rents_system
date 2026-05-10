"""
Django Management Command: Migrate Room Media
Safely migrates existing room images to new per-room directory structure
"""

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import Room, RoomImage


class Command(BaseCommand):
    help = 'Migrate existing room images to new per-room directory structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually moving files',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if files already exist in target location',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.WARNING('=== ROOM MEDIA MIGRATION ===')
        )
        self.stdout.write(
            f"Mode: {'DRY RUN - No files will be moved' if dry_run else 'LIVE - Files will be moved'}"
        )
        
        media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        
        # Migrate primary room photos
        self.stdout.write('\n--- Migrating Primary Room Photos ---')
        primary_migrated = 0
        primary_skipped = 0
        
        for room in Room.objects.all():
            if room.photo and hasattr(room.photo, 'path'):
                old_path = room.photo.path
                if os.path.exists(old_path):
                    new_path = os.path.join(media_root, room.get_primary_image_path())
                    new_dir = os.path.dirname(new_path)
                    
                    if self._should_migrate_file(old_path, new_path, force):
                        if dry_run:
                            self.stdout.write(f"  Would move: {old_path} -> {new_path}")
                            primary_migrated += 1
                        else:
                            self._move_file(old_path, new_path, new_dir, force)
                            
                            # Update database record
                            room.photo.name = room.get_primary_image_path()
                            room.save(update_fields=['photo'])
                            
                            self.stdout.write(f"  Moved: {room.room_code}")
                            primary_migrated += 1
                    else:
                        primary_skipped += 1
                        self.stdout.write(f"  Skipped: {room.room_code} (already exists)")
        
        # Migrate additional room images
        self.stdout.write('\n--- Migrating Additional Room Images ---')
        additional_migrated = 0
        additional_skipped = 0
        
        for room_image in RoomImage.objects.all():
            if room_image.image and hasattr(room_image.image, 'path'):
                old_path = room_image.image.path
                if os.path.exists(old_path):
                    new_path = os.path.join(media_root, room_image.room.get_additional_image_path(room_image.order))
                    new_dir = os.path.dirname(new_path)
                    
                    if self._should_migrate_file(old_path, new_path, force):
                        if dry_run:
                            self.stdout.write(f"  Would move: {old_path} -> {new_path}")
                            additional_migrated += 1
                        else:
                            self._move_file(old_path, new_path, new_dir, force)
                            
                            # Update database record
                            room_image.image.name = room_image.room.get_additional_image_path(room_image.order)
                            room_image.save(update_fields=['image'])
                            
                            self.stdout.write(f"  Moved: {room_image.room.room_code} - Image {room_image.order + 1}")
                            additional_migrated += 1
                    else:
                        additional_skipped += 1
                        self.stdout.write(f"  Skipped: {room_image.room.room_code} - Image {room_image.order + 1} (already exists)")
        
        # Summary
        self.stdout.write('\n=== MIGRATION SUMMARY ===')
        self.stdout.write(f"Primary Photos: {primary_migrated} migrated, {primary_skipped} skipped")
        self.stdout.write(f"Additional Images: {additional_migrated} migrated, {additional_skipped} skipped")
        self.stdout.write(f"Total: {primary_migrated + additional_migrated} files migrated")
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS('DRY RUN COMPLETED - Run with --force to actually migrate files')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('MIGRATION COMPLETED SUCCESSFULLY')
            )
    
    def _should_migrate_file(self, old_path, new_path, force):
        """Check if file should be migrated"""
        if not os.path.exists(old_path):
            return False

        if os.path.abspath(old_path) == os.path.abspath(new_path):
            return False
        
        if os.path.exists(new_path):
            return force
        
        return True

    def _move_file(self, old_path, new_path, new_dir, force):
        """Move a media file, replacing the target only when explicitly forced."""
        os.makedirs(new_dir, exist_ok=True)
        if force and os.path.exists(new_path):
            os.remove(new_path)
        shutil.move(old_path, new_path)
