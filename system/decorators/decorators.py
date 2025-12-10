import logging
from functools import wraps

from django.shortcuts import get_object_or_404, redirect

from system.models import CustomUser

logger = logging.getLogger(__name__)


def aluno_required(view_func):
    """
    Bloqueia o acesso de professores (exceto superuser).
    Elimina repetições nas views.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if user.role == "professor" and not user.is_superuser:
            logger.warning(f"Professor tentou acessar: {request.path}")
            return redirect(
                "acesso_negado", mensagem="Apenas alunos têm acesso a esta página."
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def aluno_only(view_func):
    """
    Permite o aluno acessar apenas suas próprias informações.
    Evita que alunos acessem dados de outros alunos.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        student = get_object_or_404(CustomUser, id=kwargs.get("student_id"))
        user = request.user

        if user.role == "aluno" and user != student:
            logger.warning(
                f"Aluno {user.first_name} tentou acessar dados de outro aluno: {student.first_name}"
            )
            return redirect(
                "acesso_negado",
                mensagem=f"Você não tem permissão para acessar os dados de outro aluno.",
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def professor_required(view_func):
    """
    Bloqueia o acesso de alunos (exceto superuser).
    Elimina repetições nas views.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if user.role == "aluno" and not user.is_superuser:
            logger.warning(f"Aluno tentou acessar: {request.path}")
            return redirect(
                "acesso_negado",
                mensagem=f"Apenas professores têm acesso a esta página.",
            )

        return view_func(request, *args, **kwargs)

    return wrapper
