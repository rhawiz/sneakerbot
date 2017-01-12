
document.body.innerHTML = ""

function onloadCallback(){
  grecaptcha.render('html_element', {
    'sitekey' : '6LeOnCkTAAAAAK72JqRneJQ2V7GvQvvgzsVr-6kR'
  });
};

var s=document.createElement('script');
s.type = 'text/javascript';
s.innerHTML=onloadCallback;
document.head.appendChild(s);


var form = document.createElement("form");
form.setAttribute("method", "POST");
form.setAttribute("action", "?");

var div = document.createElement("div");
div.setAttribute("id","html_element");

var input = document.createElement("input");
input.setAttribute("type","submit");
input.setAttribute("value","Submit");

form.appendChild(div);
form.appendChild(input);

document.body.appendChild(form);

var callbackScript = document.createElement("script");
callbackScript.setAttribute("src","https://www.google.com/recaptcha/api.js?onload=onloadCallback&render=explicit");
callbackScript.setAttribute("async","");
callbackScript.setAttribute("defer","");

document.body.appendChild(callbackScript);