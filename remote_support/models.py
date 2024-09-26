from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=300)
    image = models.CharField(max_length=64, default='http://127.0.0.1:9000/images/default.jpg')
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'issues'

class Appeal(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_column='client_id', related_name='client_id')
    helper = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_column='helper_id', related_name='helper_id')
    status_id = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_applied = models.DateTimeField()
    time_ended = models.DateTimeField()
    connection_code = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'appeals'

class AppealIssues(models.Model):
    id = models.AutoField(primary_key=True)
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE, db_column='appeal_id')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, db_column='issue_id')
    count = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        managed = False
        db_table = 'appeal_issues'
        unique_together = (('appeal_id', 'issue_id'),)