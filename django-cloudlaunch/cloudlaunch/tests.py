from unittest.mock import patch
import uuid

from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from djcloudbridge import models as cb_models
from rest_framework import status
from rest_framework.test import APITestCase

from . import tasks
from .models import (Application,
                     ApplicationDeployment,
                     ApplicationVersion,
                     ApplicationDeploymentTask)


# Create your tests here.
class ApplicationTests(APITestCase):

    APP_DATA = {'name': 'HelloWorldApp',
                'slug': 'helloworldapp',
                'description': 'HelloWorldDesc',
                'info_url': 'http://www.cloudlaunch.org',
                'status': 'LIVE',
                }

    def _create_application(self, app_data):
        url = reverse('application-list')
        return self.client.post(url, app_data, format='json')

    def test_create_application(self):
        """
        Ensure we can create a new application object.
        """
        response = self._create_application(ApplicationTests.APP_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(Application.objects.get().name, 'HelloWorldApp')
        self.assertEqual(Application.objects.get().slug, 'helloworldapp')

    def test_get_application(self):
        """
        Ensure we can retrieve an application object.
        """
        data = ApplicationTests.APP_DATA
        self._create_application(data)
        url = reverse('application-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset(data, response.json()['results'][0])

    def test_delete_application(self):
        """
        Ensure we can delete an application object.
        """
        data = ApplicationTests.APP_DATA
        new_app = self._create_application(data)
        url = reverse('application-detail', args=[new_app.data['slug']])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Application.objects.count(), 0)

    def test_update_application(self):
        """
        Ensure we can update an application object.
        """
        data = ApplicationTests.APP_DATA.copy()
        new_app = self._create_application(data)
        url = reverse('application-detail', args=[new_app.data['slug']])
        data['name'] = 'HelloWorldApp2'
        data['description'] = 'HelloWorldDesc2'
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Application.objects.get().name, 'HelloWorldApp2')
        self.assertEqual(Application.objects.get().description,
                         'HelloWorldDesc2')


class UserTests(APITestCase):

    LOGIN_DATA = {'username': 'TestUser',
                  'email': 'testuser@cloudlaunch.org',
                  'password': 'test_user_pass'
                  }

    REG_DATA = {'username': 'TestUser',
                'email': 'testuser@cloudlaunch.org',
                'password1': 'test_user_pass',
                'password2': 'test_user_pass'
                }

    def _register_user(self, data):
        url = reverse('rest_auth_reg:rest_register')
        return self.client.post(url, data, format='json')

    def _login_user(self, data):
        url = reverse('rest_auth:rest_login')
        response = self.client.post(url, data, format='json').json()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + response.get('key'))

    def _register_and_login(self):
        self._register_user(UserTests.REG_DATA)
        self._login_user(UserTests.LOGIN_DATA)

    def test_register_user(self):
        """
        Ensure we can register a new user.
        """
        response = self._register_user(UserTests.REG_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'TestUser')
        self.assertEqual(User.objects.get().email,
                         'testuser@cloudlaunch.org')
        self.assertIsNotNone(User.objects.get().password)

    def test_get_user(self):
        """
        Ensure we can retrieve a registered user
        """
        self._register_and_login()
        url = reverse('rest_auth:rest_user_details')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        login_sanitized = UserTests.LOGIN_DATA.copy()
        del login_sanitized['password']
        self.assertDictContainsSubset(login_sanitized, response.json())

    def test_update_user(self):
        """
        Ensure we can update a user
        """
        self._register_and_login()
        url = reverse('rest_auth:rest_user_details')
        data = UserTests.REG_DATA.copy()
        data['first_name'] = 'Mr. Test'
        data['last_name'] = 'User'
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().first_name, 'Mr. Test')
        self.assertEqual(User.objects.get().last_name, 'User')

    def test_create_cloud_creds(self):
        """
        Ensure we can update a user's stored cloud credentials
        """
        # TODO: Ensure that a user's cloud credentials can be created.
        self._register_and_login()


class DeploymentTaskTests(APITestCase):

    def _create_test_deployment(self, user):
        application = Application.objects.create(
            name="Ubuntu",
            status=Application.LIVE,
        )
        application_version = ApplicationVersion.objects.create(
            application=application,
            version="1.0",
        )
        target_cloud = cb_models.AWS.objects.create(
            name='Amazon US East 1 - N. Virginia',
            kind='cloud',
        )
        user_profile = cb_models.UserProfile.objects.create(user=user)
        credentials = cb_models.AWSCredentials.objects.create(
            cloud=target_cloud,
            access_key='access_key',
            secret_key='secret_key',
            user_profile=user_profile,
        )
        app_deployment = ApplicationDeployment.objects.create(
            owner=user,
            application_version=application_version,
            target_cloud=target_cloud,
            credentials=credentials
        )
        return app_deployment

    def setUp(self):
        """Create user and log in."""
        self.user = User.objects.create(username='test-user')
        self.client.force_authenticate(user=self.user)

    @patch("cloudlaunch.tasks.health_check.delay")
    def test_create_health_check_task(self, health_check_task):
        """Test creating a HEALTH_CHECK type task."""
        app_deployment = self._create_test_deployment(user=self.user)
        url = reverse('deployment_task-list',
                      kwargs={'deployment_pk': app_deployment.id})
        celery_id = str(uuid.uuid4())
        health_check_task.return_value = AsyncResult(celery_id)
        response = self.client.post(url, {'action': 'HEALTH_CHECK'})
        self.assertEqual(response.status_code, 201)
        health_check_task.assert_called_with(
            app_deployment.id,
            app_deployment.credentials.as_dict())
        self.assertEqual(response.data['celery_id'], celery_id)
        self.assertEqual(response.data['action'], 'HEALTH_CHECK')
        # check that ApplicationDeploymentTask was created, will throw
        # DoesNotExist if missing
        task = ApplicationDeploymentTask.objects.get(action='HEALTH_CHECK',
                                                     celery_id=celery_id,
                                                     deployment=app_deployment)
        self.assertIsNotNone(task)

    @patch("cloudlaunch.tasks.restart_appliance.delay")
    def test_create_restart_task(self, restart_task):
        """Test creating a RESTART type task."""
        app_deployment = self._create_test_deployment(user=self.user)
        url = reverse('deployment_task-list',
                      kwargs={'deployment_pk': app_deployment.id})
        celery_id = str(uuid.uuid4())
        restart_task.return_value = AsyncResult(celery_id)
        response = self.client.post(url, {'action': 'RESTART'})
        self.assertEqual(response.status_code, 201)
        restart_task.assert_called_with(
            app_deployment.id,
            app_deployment.credentials.as_dict())
        self.assertEqual(response.data['celery_id'], celery_id)
        self.assertEqual(response.data['action'], 'RESTART')
        # check that ApplicationDeploymentTask was created, will throw
        # DoesNotExist if missing
        task = ApplicationDeploymentTask.objects.get(action='RESTART',
                                                     celery_id=celery_id,
                                                     deployment=app_deployment)
        self.assertIsNotNone(task)

    @patch("cloudlaunch.tasks.delete_appliance.delay")
    def test_create_delete_task(self, delete_task):
        """Test creating a DELETE type task."""
        app_deployment = self._create_test_deployment(user=self.user)
        url = reverse('deployment_task-list',
                      kwargs={'deployment_pk': app_deployment.id})
        celery_id = str(uuid.uuid4())
        delete_task.return_value = AsyncResult(celery_id)
        response = self.client.post(url, {'action': 'DELETE'})
        self.assertEqual(response.status_code, 201)
        delete_task.assert_called_with(
            app_deployment.id,
            app_deployment.credentials.as_dict())
        self.assertEqual(response.data['celery_id'], celery_id)
        self.assertEqual(response.data['action'], 'DELETE')
        # check that ApplicationDeploymentTask was created, will throw
        # DoesNotExist if missing
        task = ApplicationDeploymentTask.objects.get(action='DELETE',
                                                     celery_id=celery_id,
                                                     deployment=app_deployment)
        self.assertIsNotNone(task)

    def test_only_one_launch_task(self):
        """Test LAUNCH task not allowed if one already exists."""
        app_deployment = self._create_test_deployment(user=self.user)
        ApplicationDeploymentTask.objects.create(
            deployment=app_deployment,
            action=ApplicationDeploymentTask.LAUNCH)
        self.assertEqual(
            len(ApplicationDeploymentTask.objects.filter(
                deployment=app_deployment,
                action=ApplicationDeploymentTask.LAUNCH)),
            1,
            "Only one LAUNCH task should exist.")
        url = reverse('deployment_task-list',
                      kwargs={'deployment_pk': app_deployment.id})
        response = self.client.post(url, {'action': 'LAUNCH'})
        self.assertEqual(response.status_code, 400)
        self.assertTrue('action' in response.data)
        # LAUNCH task count is still 1
        self.assertEqual(
            len(ApplicationDeploymentTask.objects.filter(
                deployment=app_deployment,
                action=ApplicationDeploymentTask.LAUNCH)),
            1,
            "Only one LAUNCH task should exist.")
