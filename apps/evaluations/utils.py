from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from .models import AuditLog


def render_to_pdf(template_src, context_dict={}, filename="reporte.pdf"):
    """
    Renderiza una plantilla HTML de Django a un archivo PDF descargable usando xhtml2pdf.
    """
    try:
        from xhtml2pdf import pisa
    except ImportError:
        print("Advertencia: xhtml2pdf no está instalado en este entorno.")
        return None

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Renderizar HTML a PDF en UTF-8
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return None



def log_action(user, action, model_name, object_id, changes=None, request=None):
    """
    Registra una acción inmutable en la bitácora de auditoría (AuditLog).
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    try:
        AuditLog.objects.create(
            user=user if (user and user.is_authenticated) else None,
            action=action,
            model_name=model_name,
            object_id=object_id if object_id else 0,
            changes=changes or {},
            ip_address=ip_address
        )
    except Exception as e:
        # Evitar interrumpir el flujo principal si ocurre un error de auditoría
        print(f"Error al guardar AuditLog: {e}")
