function getCodeEditorUserLBUI(ev){
    const userSelectLogicBlockBVal =  document.getElementById(ev).value;
    if(userSelectLogicBlockBVal){
        fetch(`${userSelectLogicBlockBVal}/get_code_editor_ui`,{
            method:'GET',
            headers:{
                "Content":"application/json",
                'X-CSRFToken': getCSRFToken()
            },
        })
        .then(res=>res.json())
        .then(data=>{
            if(data['status'] == 'success'){
                console.log(data);
                codeEditorURL = data['code_editor_url'];
                window.location = codeEditorURL;
            }
        })
        .catch(error=>console.log("Error",error))
    }
    else{
        alert("please select a logic block to enter code")
    }
}

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}