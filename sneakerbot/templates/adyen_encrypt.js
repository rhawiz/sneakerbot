
//
//function adyenEncrypt(cardNumber, cvc, holderName, expiryMonth, expiryYear, generationtime, key) {
//
//    var options = {};
//
//    var cseInstance = adyen.encrypt.createEncryption(key, options);
//
//    var postData = {};
//
//    var cardData = {
//        number : cardNumber,
//        cvc : cvc,
//        holderName : holderName,
//        expiryMonth : expiryMonth,
//        expiryYear : expiryYear,
//        generationtime : generationtime
//    };
//
//    encryptedData = cseInstance.encrypt(cardData);
//
//    var d = document.getElementById("encrypted")
//    d.setAttribute("value",encryptedData)
//
//    // AJAX call or different handling of the post data
//
//}

function pad(num, size) {
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}



var s1 = document.createElement("script");
s1.setAttribute("type", "text/javascript");
s1.setAttribute("src", "adyen.encrypt.nodom.min.js");

document.head.appendChild(s1);


var s2 = document.createElement("script");
s2.setAttribute("type", "text/javascript");
s2.innerHTML = adyenEncrypt;

document.head.appendChild(s2);

var f = document.createElement("input");
f.setAttribute("id","fingerprint");
f.setAttribute("value","");

document.body.appendChild(f);


var s3 = document.createElement("script");
s3.setAttribute("type", "text/javascript");

var now = new Date();
var MM = pad(now.getMonth()+1, 2);
var DD =  pad(now.getDate(), 2);
var YYYY = now.getFullYear();

s3.setAttribute("src", "https://live.adyen.com/hpp/js/df.js?v="+YYYY+MM+DD);
document.body.appendChild(s3);


//var s4 = document.createElement("script")
//s4.innerHTML = dfDo("fingerprint");
//
////document.body.appendChild(s4)
//
//var d = document.createElement("div")
//d.setAttribute("id","encrypted")
//document.body.appendChild(d)