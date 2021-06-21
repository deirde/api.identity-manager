# API-IDENTITY-MANAGER

Simple Python Flask based API with password and token based authentication.<br/>
<br/>
Purpose of the API:<br/>
. Track API usage by user</br>
. Token based authentication<br/>
. One time tokens for query based actions<br/>
. Expose and update user data<br/>
. Keep historical data<br/>
. Blacklist feature<br/>
<br/>
Endpoints provided:<br/>
<i>. /v1/account/signup/</i>: Register the user and set the account<br/>
<i>. /v1/account/activate/</i>: Activate the user account<br/>
<i>. /v1/account/authenticate/</i>: Authenticate the user providing a valid token<br/>
<i>. /v1/account/authorize/</i>: Authorize the token returning the user identity<br/>
<i>. /v1/account/ott_generate/</i>: One-time token generation<br/>
<i>. /v1/account/ott_authorize/</i>: One-time token authorization<br/>
<i>. /v1/account/update_email/</i>: Update the user email<br/>
<i>. /v1/account/update_password/</i>: Update the user password<br/>
<i>. /v1/account/get_registry/</i>: Expose the user personal data<br/>
<i>. /v1/account/update_registry/</i>: Update the user personal data<br/>
