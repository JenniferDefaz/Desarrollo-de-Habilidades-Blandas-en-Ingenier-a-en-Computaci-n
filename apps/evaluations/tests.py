from django.test import TestCase, RequestFactory
from apps.users.models import CustomUser, Role, SystemSetting, SupportTicket
from apps.competencies.models import Competency, Subcompetency
from apps.evaluations.models import AuditLog, GraduateFeedback
from apps.evaluations.utils import render_to_pdf, log_action
from apps.evaluations.views import (
    audit_log_list, wellness_alerts, export_my_report_pdf,
    graduate_feedback_create, graduate_feedback_list
)
from apps.users.views import system_settings_view, support_ticket_list
from apps.notifications.utils import send_notification_email


class NewFeaturesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Crear roles
        self.role_admin, _ = Role.objects.get_or_create(name='ADMINISTRADOR')
        self.role_student, _ = Role.objects.get_or_create(name='ESTUDIANTE')
        self.role_bienestar, _ = Role.objects.get_or_create(name='BIENESTAR_UNIVERSITARIO')
        self.role_graduado, _ = Role.objects.get_or_create(name='GRADUADO')
        
        # Crear usuarios
        self.admin_user = CustomUser.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            role=self.role_admin
        )
        self.student_user = CustomUser.objects.create_user(
            username='student_test',
            email='student@test.com',
            password='password123',
            role=self.role_student
        )
        self.bienestar_user = CustomUser.objects.create_user(
            username='bienestar_test',
            email='bienestar@test.com',
            password='password123',
            role=self.role_bienestar
        )
        self.graduado_user = CustomUser.objects.create_user(
            username='graduado_test',
            email='graduado@test.com',
            password='password123',
            role=self.role_graduado
        )
        
        # Crear Competencias
        self.competency = Competency.objects.create(
            name='Comunicación Asertiva',
            description='Habilidad para comunicarse eficazmente.'
        )

    def test_log_action_creates_audit_log(self):
        """Verifica que log_action cree un registro inmutable en AuditLog."""
        log_action(
            user=self.admin_user,
            action='TEST_ACTION',
            model_name='CustomUser',
            object_id=self.student_user.id,
            changes={'test_key': 'test_val'}
        )
        log = AuditLog.objects.filter(action='TEST_ACTION').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.admin_user)

    def test_system_settings_model_and_view(self):
        """Verifica la obtención de SystemSetting y acceso a la vista."""
        settings_obj = SystemSetting.get_settings()
        self.assertEqual(settings_obj.max_file_size_mb, 10)

        request = self.factory.get('/usuarios/configuracion-general/')
        request.user = self.admin_user
        response = system_settings_view(request)
        self.assertEqual(response.status_code, 200)

    def test_support_ticket_creation_and_view(self):
        """Verifica la creación de un ticket de soporte técnico."""
        ticket = SupportTicket.objects.create(
            user=self.student_user,
            subject='Error de inicio de sesión',
            description='No puedo ingresar desde mi celular',
            category=SupportTicket.Category.CUENTA
        )
        self.assertEqual(ticket.status, SupportTicket.Status.ABIERTO)

        request = self.factory.get('/usuarios/soporte/')
        request.user = self.admin_user
        response = support_ticket_list(request)
        self.assertEqual(response.status_code, 200)

    def test_graduate_feedback_model_and_views(self):
        """Verifica el módulo de retroalimentación de graduados (RF12)."""
        feedback = GraduateFeedback.objects.create(
            graduate=self.graduado_user,
            company_name='Empresa Test',
            job_title='Analista',
            competency=self.competency,
            relevance_rating=5,
            frequency_rating=4,
            feedback_text='Muy importante en el trabajo.'
        )
        self.assertIsNotNone(feedback.id)

        request = self.factory.get('/evaluaciones/graduados/respuestas/')
        request.user = self.admin_user
        response = graduate_feedback_list(request)
        self.assertEqual(response.status_code, 200)

    def test_send_notification_email(self):
        """Verifica que el despachador de emails se ejecute sin excepciones."""
        result = send_notification_email(
            recipient_email='test@ejemplo.com',
            subject='Prueba Notificación',
            message='Mensaje de prueba'
        )
        self.assertTrue(result)
