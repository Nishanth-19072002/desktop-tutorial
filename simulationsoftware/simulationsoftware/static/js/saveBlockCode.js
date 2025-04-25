document.getElementById("saveCodeBtn").addEventListener("click",saveBlockDetails);
function saveBlockDetails(){
    const codeType = document.getElementById("code-type").value;
    console.log(codeType); 
    const processingEditor = window.processingEditor;
    const code = processingEditor.getValue();
    if(codeType !== 'null'){
        if(code.trim() !== ''){
            if(codeType === 'design'){
                fetch('put_LB_design_Code',{
                    method:'POST',
                    headers:{
                        "Content":"application/json",
                        'X-CSRFToken': getCSRFToken()
                    },
                    body:JSON.stringify({
                        "LBCode" : code
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    if(data["status"] == 'success'){
                        window.location.href = "http://127.0.0.1:8000/admin_panel/"
                    }
                })
                .catch(error => console.log("Error",error));
            }
            else if(codeType === 'performance'){
                fetch('put_LB_performance_Code',{
                    method:'POST',
                    headers:{
                        "Content":"application/json",
                        'X-CSRFToken': getCSRFToken()
                    },
                    body:JSON.stringify({
                        "LBCode" : code
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    if(data["status"] == 'success'){
                        window.location.href = "http://127.0.0.1:8000/admin_panel/"
                    }
                })
                .catch(error => console.log("Error",error));
            }
            else if(codeType === 'lifing'){
                fetch('put_LB_Lifing_Code',{
                    method:'POST',
                    headers:{
                        "Content":"application/json",
                        'X-CSRFToken': getCSRFToken()
                    },
                    body:JSON.stringify({
                        "LBCode" : code
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    if(data["status"] == 'success'){
                        window.location.href = "http://127.0.0.1:8000/admin_panel/"
                    }
                })
                .catch(error => console.log("Error",error));
            }
            else{
                fetch('put_LB_Prognostic_Code',{
                    method:'POST',
                    headers:{
                        "Content":"application/json",
                        'X-CSRFToken': getCSRFToken()
                    },
                    body:JSON.stringify({
                        "LBCode" : code
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    if(data["status"] == 'success'){
                        window.location.href = "http://127.0.0.1:8000/admin_panel/"
                    }
                })
                .catch(error => console.log("Error",error));
            }
        }
        else{
            alert("please enter the code");
            return;
        }
    }
    else{
        alert("please select code type");
    }
}
function getCSRFToken(){
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}