
document.body.innerHTML = ""
document.title = "Recaptcha Harvest (fuck you adidas)"
document.body.style.height = window.innerHeight + 'px';
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

form.appendChild(div);

document.body.appendChild(form);

var callbackScript = document.createElement("script");
callbackScript.setAttribute("src","https://www.google.com/recaptcha/api.js?onload=onloadCallback&render=explicit");
callbackScript.setAttribute("async","");
callbackScript.setAttribute("defer","");

document.body.appendChild(callbackScript);