from ragendja.settings_post import settings

settings.add_app_media('combined-%(LANGUAGE_CODE)s.js',
    'pingpong/core.js',
    'pingpong/jquery-ui-1.8.custom.min.js',
)
settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'pingpong/core.css',
    'pingpong/jquery-ui-1.8.custom.css',
)
