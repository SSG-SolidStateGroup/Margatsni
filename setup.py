import os
### Things that are commented are things I'm not sure what they do yet (- Ismail A.)
setup(
    name='Margasni',
    version='1.0',
    url='http://cs480-projects.github.io/teams-fall2017/SSG/index.html',
    author='Solid State Group',
    # author_email='foundation@djangoproject.com',
    description=('An Instagram photo download tool),
    # license='BSD',
    # packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    # scripts=['django/bin/django-admin.py'],
    # entry_points={'console_scripts': [
        'django-admin = django.core.management:execute_from_command_line',
    ]},
    # install_requires=['pytz'],
    # extras_require={
    #   "bcrypt": ["bcrypt"],
    #    "argon2": ["argon2-cffi >= 16.1.0"],
    # },
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Instagram Users',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
