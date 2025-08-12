## oauth2 authentication sequence with curl

It could be quite tricky to debug issues in the oauth2 authentication sequence, so I created a script which is performing the steps one by one using curl.
The following example works for oauth2-proxy => hydra => IDP flow, depending on the softwares used the parameters and handling can change.

```
#!/bin/bash

url="$1"
u="$2"
p="$3"

CK="/tmp/cookies.txt"
curl_get_redirect=(-b "$CK" -c "$CK" -w "%{redirect_url}\n" -s -o /dev/null -k)

rm -f "$CK" && touch "$CK"
auth_loc=$(curl "${curl_get_redirect[@]}" "${url}")
echo "first redirect: $auth_loc (to OAuth 2.0 and OpenID Connect Provider)"

login_loc=$(curl "${curl_get_redirect[@]}" "${auth_loc}")
echo "2nd redirect to idp: $login_loc => fetching csrf value first"

login_load=$(curl -c "$CK" -b "$CK" -k "$login_loc" -o /tmp/login.html)
login_challenge=$(echo "$login_loc" | grep -oP 'login_challenge=\K[^&]+')
csrf_token=$(grep -oP 'name="_csrf"\s+value="\K[^"]+' /tmp/login.html)

login_loc=$(echo "$login_loc" | cut -d "?" -f 1) # remove url parameters, payload will be POSTed
echo "2nd redirect to idp: $login_loc => login using csrf_token=$csrf_token"
next_loc=$(curl "${curl_get_redirect[@]}" -X POST "$login_loc" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "remember=0" \
  --data-urlencode "submit=Log+in" \
  --data "challenge=${login_challenge}" \
  --data-urlencode "_csrf=${csrf_token}" \
  --data-urlencode "$u" \
  --data-urlencode "$p" )

echo "3rd redirect from idp to oauth2 provider: $next_loc"; echo
consent_loc=$(curl "${curl_get_redirect[@]}" "${next_loc}")

echo "4th redirect from oauth2 provider to consent: $consent_loc"; echo
login_challenge=$(echo "$consent_loc" | grep -oP 'consent_challenge=\K[^&]+' | sed -e 's/%3D/=/g')

echo "4th redirect from oauth2 provider to consent:  login_challenge=$login_challenge"; echo
oauth_loc=$(curl "${curl_get_redirect[@]}" -X POST "${consent_loc}" -H "Content-Type: application/json" \
  -d '{
    "challenge": "'$login_challenge'",
    "_csrf": "'$csrf_token'",
    "grant_scope": ["email", "openid"],
    "remember": true,
    "submit": "Allow access"
}')

echo; echo; echo "5ths redirect from idp to oauth2: $oauth_loc"
callback_loc=$(curl "${curl_get_redirect[@]}" "${oauth_loc}" )

echo; echo; echo "6ths redirect to callback: $callback_loc"
final_loc=$(curl "${curl_get_redirect[@]}" "${callback_loc}" )

echo; echo; echo "7ths redirect to final service: $final_loc"
curl -b "$CK" -c "$CK" -k -v "$final_loc"

```
