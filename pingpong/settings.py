from ragendja.settings_post import settings

settings.add_app_media('combined-%(LANGUAGE_CODE)s.js',
    'pingpong/jquery.validationEngine-en.js',
	'pingpong/jquery.validationEngine.js',
	'pingpong/core.js',
    'pingpong/jquery-ui-1.8.custom.min.js',
)
settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'pingpong/validationEngine.jquery.css',
	'pingpong/core.css',
    'pingpong/jquery-ui-1.8.custom.css',
)
settings.add_app_media('ie.css',
    'pingpong/ie.css',
)
