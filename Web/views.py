from django.shortcuts import render
from Web.models import Issue, Appeal, AppealIssues
import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname='web',
    user='web_user',
    password='123123',
    host='localhost',
    port=5432
)
cur = conn.cursor()

activeUserId = 1

def getActiveAppealForUser(userId):
    return Appeal.objects.filter(client_id=userId, status_id=1).first()

def deleteAppealForUser(userId):
    cur.execute('SELECT id FROM appeals WHERE client_id = %s AND status_id = 1 LIMIT 1', (userId,))
    appealId = cur.fetchone()
    if appealId != None:
        cur.execute('UPDATE appeals SET status_id = 2, time_ended=CURRENT_TIMESTAMP WHERE id = %s', (appealId,))
    conn.commit()

def addIssueToAppealForUser(userId, issueId, count=1):
    appeal = getActiveAppealForUser(userId)
    if appeal == None:
        appeal = Appeal.objects.create(client_id=userId, status_id=1)
    AppealIssues.objects.get_or_create(appeal_id=appeal.id, issue_id=issueId, defaults={'count': count})

def getAppealIssuesById(appealId):
    return AppealIssues.objects.filter(appeal_id=appealId).all()

def getAppealByIdForUser(appealId, userId):
    return Appeal.objects.get(id=appealId, client_id=userId, status_id=1)

def getIssueById(id):
    try:
        return Issue.objects.get(id=id)
    except Issue.DoesNotExist:
        return None

def getIssuesContaining(name):
    return Issue.objects.filter(name__icontains=name, is_active=True).all()

# Index controller
def indexController(request):
    appealAmount = 0
    userAppealId = -1
    issuesInCurrentAppeal = []
    appeal = getActiveAppealForUser(activeUserId)

    if appeal != None:
        issuesInCurrentAppeal = getAppealIssuesById(appeal.id)
        appealAmount = len(issuesInCurrentAppeal)
        userAppealId = appeal.id

    search = ''
    if 'issue_name' in request.GET:
        search = request.GET['issue_name']

    data = {
        'issues': [],
        'appealAmount': appealAmount,
        'search': search,
        'userAppealId': userAppealId
    }

    for issue in getIssuesContaining(search):
        canAdd = True
        for addedIssue in issuesInCurrentAppeal:
            if issue.id == addedIssue.issue_id:
                canAdd = False
                break
        data['issues'].append({
            'data': issue,
            'canAdd': canAdd
        })

    return render(request, 'index.html', data)

# Issue controller
def issueController(request, id):
    issue = getIssueById(id)
    if issue == None:
        return indexController(request)

    return render(request, 'issue.html', {
        'issue': issue
    })

def issueAddController(request, id):
    issue = getIssueById(id)
    if issue == None:
        return indexController(request)

    addIssueToAppealForUser(activeUserId, id)

    return indexController(request)

# Appeal controller
def appealController(request, appealId):
    appeal = getAppealByIdForUser(appealId, activeUserId)
    if appeal == None:
        return indexController(request)

    issues = getAppealIssuesById(appealId)

    data = {
        'issues': []
    }
    for issueData in issues:
        issue = getIssueById(issueData.issue_id)
        if issue != None:
            data['issues'].append({
                'name': issue.name,
                'image': issue.image,
                'count': issueData.count
            })

    return render(request, 'appeal.html', data)

def appealDeleteController(request):
    deleteAppealForUser(activeUserId)
    return indexController(request)