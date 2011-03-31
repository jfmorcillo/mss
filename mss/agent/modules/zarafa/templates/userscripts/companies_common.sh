# shell include script

ZARAFA_LANG="${ZARAFA_USERSCRIPT_LOCALE:-${LC_MESSAGES:-en_US}}"
PATH=/bin:/usr/local/bin:/usr/bin
export ZARAFA_LANG PATH

if [ -z "${ZARAFA_COMPANY_SCRIPTS}" ] ; then
    exec >&2
    echo "Do not execute this script directly"
    exit 1
fi

if [ ! -d "${ZARAFA_COMPANY_SCRIPTS}" ] ; then
    exec >&2
    echo "${ZARAFA_COMPANY_SCRIPTS} does not exist or is not a directory"
    exit 1
fi

if [ -z "${ZARAFA_COMPANY}" -a -z "${ZARAFA_COMPANYID}" ] ; then
    exec >&2
    echo "ZARAFA_COMPANY and ZARAFA_COMPANYID is not set."
    exit 1
fi

find ${ZARAFA_COMPANY_SCRIPTS} -maxdepth 1 -type f -perm -u=x -not -name \*~ -not -name \#\* -not -name \*.rpm\* -not -name \*.bak -not -name \*.old -exec {} \;
