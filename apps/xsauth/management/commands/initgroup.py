from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission,ContentType,Group
from apps.novel.models import Novel,NovelChapter,NovelCategory,NovelTag,Banner,Advertisement,ExcellentWorks
from django.db.models import Q


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 作家组
        author_codenames = [
            'add_novel',
            'change_novel',
            'delete_novel',
        ]
        author_content_types = [
            ContentType.objects.get_for_model(NovelChapter),
        ]
        author_permissions = Permission.objects.filter(Q(codename__in=author_codenames)|Q(content_type__in=author_content_types))
        author_group = Group.objects.create(name='作家')
        author_group.permissions.set(author_permissions)
        author_group.save()
        self.stdout.write(self.style.SUCCESS('作家组创建成功'))


        # 广告组
        advertisement_content_types = [
            ContentType.objects.get_for_model(Banner),
            ContentType.objects.get_for_model(Advertisement),
            ContentType.objects.get_for_model(ExcellentWorks)
        ]
        advertisement_permissions = Permission.objects.filter(content_type__in=advertisement_content_types)
        advertisement_group = Group.objects.create(name='广告')
        advertisement_group.permissions.set(advertisement_permissions)
        advertisement_group.save()
        self.stdout.write(self.style.SUCCESS('广告组创建成功'))


        # 管理组
        admin_codenames = [
            'change_novel',
            'delete_novel',
            'recommand_novel',
            'change_novelchapter',
            'delete_novelchapter',
        ]
        # 小说
        admin_permissions = Permission.objects.filter(codename__in=admin_codenames)
        admin_content_types = [
            ContentType.objects.get_for_model(NovelCategory),
            ContentType.objects.get_for_model(NovelTag),
        ]
        # 标签 分类
        admin_permissions = admin_permissions.union(Permission.objects.filter(content_type__in=admin_content_types))
        # 广告
        admin_permissions.union(advertisement_permissions)
        admin_group = Group.objects.create(name='管理')
        admin_group.permissions.set(admin_permissions)
        admin_group.save()
        self.stdout.write(self.style.SUCCESS('管理组创建成功'))

