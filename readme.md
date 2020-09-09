# API.ACCOUNT.WEBFORYOU.TV #

Python Flask based API with a password and timed token-based authentication.<br/>
<br/>
Purpose of the API:<br/>
. Track API usage managing quotas</br>
. Implement user token based authentication<br/>
. Generation and authorizaion of one time tokens for query based actions<br/>
. Expose user data<br/>
. Update user data<br/>
. Keep historical data<br/>
. Blacklist feature<br/>
. Fast answer<br/>
. High security layer<br/>
. Unit tests<br/>
. Load tests<br/>
<br/>
The endpoints:<br/>
<i>. /v1/account/signup/</i>: Check the existance of the provided email, register the new user and set the account as inactive<br/>
<i>. /v1/account/activate/</i>: Activate the user from its hashed portion of data<br/>
<i>. /v1/account/authenticate/</i>: Authenticate the user email and password giving back a valid timed token<br/>
<i>. /v1/account/authorize/</i>: Authorize the provided token returning the user identity<br/>
<i>. /v1/account/ott_generate/</i>: One-time token generation for query based actions<br/>
<i>. /v1/account/ott_authorize/</i>: One-time token authorization<br/>
<i>. /v1/account/update_email/</i>: Update the user email, set the account as inactive and store the changes history<br/>
<i>. /v1/account/update_password/</i>: Update the user password, set the account as inactive and store the changes history<br/>
<i>. /v1/account/get_registry/</i>: Expose the user personal registry containing generic and non sensible personal data<br/>
<i>. /v1/account/update_registry/</i>: Update the user personal registry<br/>
<br/>
<b>Project still on development</b>.