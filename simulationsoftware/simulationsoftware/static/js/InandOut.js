function makeDataInBlock(blockId){
    blockIdElement = document.getElementById(blockId);
    dataInblock = document.createElement('div');
        dataInblock.id = blockId+"_"+blockIdElement.getAttribute("mode")+"-" +"in";
        blockIdElement.appendChild(dataInblock)
    dataInblock.addEventListener("click",(event)=>{
        makeConnection(event)
    })
    dataInblock.style.width = "7px";
    dataInblock.style.height = "7px";
    dataInblock.style.border = "1px solid black";
    dataInblock.style.position = "absolute";
    dataInblock.style.left = "-7px";
    dataInblock.style.top = "20px";
    dataInblock.style.borderRadius = "30%";
}
function makeDataOutBlock(blockId){
    let width = document.getElementById(blockId).getBoundingClientRect().width;
    blockIdElement = document.getElementById(blockId);
    dataOutblock = document.createElement('div');
    dataOutblock.id = blockId+"_"+blockIdElement.getAttribute("mode")+"-" +"out";
    blockIdElement.appendChild(dataOutblock)
    dataOutblock.addEventListener("click",(event)=>{
        startConnection(event)
    })
    dataOutblock.style.width = "7px";
    dataOutblock.style.height = "7px";
    dataOutblock.style.border = "1px solid black";
    dataOutblock.style.position = "absolute";
    dataOutblock.style.left = (width) +"px";
    dataOutblock.style.top = "20px";
    dataOutblock.style.borderRadius = "30%";
}