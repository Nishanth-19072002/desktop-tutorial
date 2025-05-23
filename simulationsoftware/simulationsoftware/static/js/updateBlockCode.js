function get_code(ev){
    const processingEditor = window.processingEditor;
    const codeType = ev.value;
    if(codeType === 'design'){
        fetch("get_design_code",{
            method:'GET',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    processingEditor.setValue(data['code']);
                }
            })
        .catch(error => console.log("Error",error));
    }
    else if(codeType === 'performance'){
        fetch("get_performance_code",{
            method:'GET',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    processingEditor.setValue(data['code']);
                }
            })
        .catch(error => console.log("Error",error));
    }
    else if(codeType === 'lifing'){
        fetch("get_lifing_code",{
            method:'GET',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    processingEditor.setValue(data['code']);
                }
            })
        .catch(error => console.log("Error",error));
    }
    else{
        fetch("get_prognostic_code",{
            method:'GET',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    processingEditor.setValue(data['code']);
                }
            })
        .catch(error => console.log("Error",error));
    }
}
function put_edited_code(ev){
    const codeType = document.getElementById(ev).value;
    if(codeType == 'design'){
        fetch('put_design_edited_code',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "code": processingEditor.getValue()
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    window.location = data['admin_url'];
                }
            })
        .catch(error => console.log("Error",error));
    }
    else if(codeType == 'performance'){
        fetch('put_performance_edited_code',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "code": processingEditor.getValue()
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    window.location = data['admin_url'];
                }
            })
        .catch(error => console.log("Error",error));
    }
    else if(codeType == 'lifing'){
        fetch('put_lifing_edited_code',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "code": processingEditor.getValue()
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    window.location = data['admin_url'];
                }
            })
        .catch(error => console.log("Error",error));
    }
    else{
        fetch('put_prognostic_edited_code',{
            method:'POST',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
            body:JSON.stringify({
                "code": processingEditor.getValue()
            })
        })
        .then(response => response.json())
        .then(data => {
            if(data["status"] == 'success'){
                    window.location = data['admin_url'];
                }
            })
        .catch(error => console.log("Error",error));
    }
}

function getCSRFToken(){
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

