var messagejson;


function encodeString(string) {
  var encoder = new TextEncoder();
  return encoder.encode(string);
}
function decodeString(encoded) {
  var decoder = new TextDecoder();
  return decoder.decode(encoded);
}

function publicKeyEncrypt() {
    let userTopublicKey = document.getElementById('thispublicKey').textContent;
    userTopublicKey = userTopublicKey.slice(2,-3);
    console.log(userTopublicKey);
    pubkeyjwk = JSON.parse(userTopublicKey);
    console.log(pubkeyjwk);
    return window.crypto.subtle.importKey(
    "jwk",
    pubkeyjwk,
    {
        name: "RSA-OAEP",
        hash: "SHA-256"
    },
    true,
    ["encrypt"]
    );
}

async function encrypt() {
    publicKeyEncrypt().then(async function(publicKey) {
        let usermsg = document.getElementById('usermsg').value;
        let username = document.getElementById('username').textContent;
        let messagetosend = "From " + username + ": " + usermsg;
        console.log("Encoding message");
        var encoded = encodeString(messagetosend);
        console.log(encoded);
        console.log(publicKey);
        let encrypted = await window.crypto.subtle.encrypt(
          {
              name: "RSA-OAEP",
              hash: "SHA-256"
          },
          publicKey,
          encoded
        );
        console.log(encrypted)
        let encryptedstring = convertArrayBufferToBase64(encrypted);
        let userto = document.getElementById('userto').textContent;
        console.log(userto);
        let messagetojson = userto + ":" + encryptedstring;
        var messagejson = JSON.stringify(messagetojson);
        $.ajax({
            url: "/chatsuccessful",
            type: "POST",
            data: JSON.stringify(messagejson),
            contentType: "application/json",
            success: function() {
                console.log("Feedback successfully stored in the server!");
            },
            error: function() {
                console.log("Feedback failed to store back in the server!");
            },
        });
    })
}

function privateKeyDecrypt(myPrivateKey, data) {
  return window.crypto.subtle.decrypt(
    {
        name: "RSA-OAEP",
        hash: "SHA-256"
    },
    myPrivateKey,
    data
  );
}

function storeInDatabase(privateKey) {

    var open = indexedDB.open("MyDatabase", 1);
    open.onsuccess = function() {
        var db = open.result;
        var tx = db.transaction("MyObjectStore", "readwrite");
        var store = tx.objectStore("MyObjectStore");

        store.put({id: 1, key: privateKey});


        tx.oncomplete = function() {
            db.close();
        };
    }
}

async function getKeysandStore() {
    var indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB || window.shimIndexedDB;

    var open = indexedDB.open("MyDatabase", 1);

    open.onupgradeneeded = function() {
        var db = open.result;
        var store = db.createObjectStore("MyObjectStore", {keyPath: "id"});
    };
    const {publicKey, privateKey} = await getKey();
    let message = "hello";

    const publicjwk = await window.crypto.subtle.exportKey('jwk', publicKey);
    console.log(publicKey);
    console.log(privateKey);
    console.log(publicjwk)
    console.log(typeof publicjwk['n']);
    var jsonString = JSON.stringify(publicjwk);
    console.log(jsonString);
    storeInDatabase(privateKey);
    $.ajax({
        url: "/validlogin",
        type: "POST",
        data: JSON.stringify(jsonString),
        contentType: "application/json",
        success: function() {
            console.log("Feedback successfully stored in the server!");
        },
        error: function() {
            console.log("Feedback failed to store back in the server!");
        },
    });
}

async function getKey() {
    let {publicKey, privateKey} = await window.crypto.subtle.generateKey(
        {
        name: "RSA-OAEP",
        modulusLength: 4096,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: "SHA-256",
        },
    true, // <== Here if you want it to be exportable !!
    ["encrypt", "decrypt"] // usage
    );
    return {publicKey, privateKey}
}

function convertArrayBufferToBase64(arrayBuffer) {
  return btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
}

function convertBase64ToArrayBuffer(base64) {
  return (new Uint8Array(atob(base64).split('').map(char => char.charCodeAt()))).buffer;
}
