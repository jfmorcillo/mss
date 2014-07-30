#!/bin/bash
 export MSG_POSTGRESQL_GET_INFORESEAUSUBNET="Entrez les informations subnet et réseau (Format : xxx.xxx.xxx.xxx/xx)"

    while [ 1 ]
            do
                echo "$MSG_POSTGRESQL_GET_INFORESEAUSUBNET"
                adressereseau="127.0.0.0/32"
                ipreseau=`echo ${adressereseau}|cut -f1,1 -d'/'`
                echo "${ipreseau}"|grep -Eq '^(([01]?[0-9]?[0-9]|2([0-4][0-9]|5[0-5]))\.){3}([01]?[0-9]?[0-9]|2([0-4][0-9]|5[0-5]))$'
                if [ $? -ne 0 ]; then
                    # obligation de definir un certain nombre de messages ici (pour que le $ipreseau soit compris !!)
                    if [ $language = "fr" ]
                    then
                        export MSG_INCORRECT_IP="adresse ip [${ipreseau}] invalide"
                    else
                        export MSG_INCORRECT_IP="Ip address [${ipreseau}] is invalid"
                    fi
                    echo $MSG_INCORRECT_IP
                else
                    echo OK
                    # format OK
                    break
                fi
            done
