function Verify() {
    this.init = function() {
        if (typeof idp !== 'undefined') {
            if(false){
                if (typeof idp.onProofChanged === 'function') {
                    idp.onProofChanged();
                }
            }

            var xhr = createCORSRequest('GET', 'https://verify.nature.com/verify/status');

            if (xhr !== null && xhr instanceof XMLHttpRequest)  {
                performAjaxRequest(xhr);
            } else {
                handleUnsupportedAjax(xhr);
            }
        }
    };

    function performAjaxRequest(xhr) {
        xhr.onreadystatechange = function () {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                if (xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    if (typeof idp.hasNatureUserProof === 'function') {
                        idp.hasNatureUserProof(data.natureUserProofExists);
                    }

                    if (typeof idp.institutionalLogin === 'function') {
                        idp.institutionalLogin(data.institutionNames);
                    }

                    if (typeof idp.ejpProofs === 'function') {
                        idp.ejpProofs(data.ejpProofs);
                    }
                } else {
                    if (typeof idp.ajaxError === 'function') {
                        idp.ajaxError(xhr.status);
                    }
                }
            }
        };
        xhr.send();
    }

    function handleUnsupportedAjax(xhr) {
        if (typeof idp.ajaxNotSupported === 'function'){
            if (xhr === null) {
                idp.ajaxNotSupported('Ajax is not supported.');
            } else {
                idp.ajaxNotSupported('Ajax with cookies is not supported.');
            }
        }
    }

    function createCORSRequest(method, url) {
        var xhr = new XMLHttpRequest();

        if ("withCredentials" in xhr) {
            xhr.open(method, url, true);
            xhr.withCredentials = true;
        } else if (typeof XDomainRequest != "undefined") {
            xhr = new XDomainRequest();
        } else {
            xhr = null;
        }

        return xhr;
    }
}

new Verify().init();

