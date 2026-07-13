def usuario_grado(request):
    ctx = {
        'user_grado': 'v4',
        'user_nivel': 4,
        'es_v00': False,
        'es_v1': False,
        'es_v2': False,
        'es_v3': False,
        'es_v4': True,
        'puede_gestionar_usuarios': False,
        'puede_editar_productos': False,
    }
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            ctx['user_grado'] = profile.grado
            ctx['user_nivel'] = profile.nivel
            ctx['es_v00'] = profile.grado == 'v00'
            ctx['es_v1'] = profile.grado == 'v1'
            ctx['es_v2'] = profile.grado == 'v2'
            ctx['es_v3'] = profile.grado == 'v3'
            ctx['es_v4'] = profile.grado == 'v4'
            ctx['puede_gestionar_usuarios'] = profile.tiene_acceso('v2')
            ctx['puede_editar_productos'] = profile.puede_publicar
        except Exception:
            pass
    return ctx
