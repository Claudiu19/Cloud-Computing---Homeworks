document.getElementById('btn').addEventListener('click', function(e){
    e.preventDefault()
    behaviour()
    e.stopPropagation()
})

function behaviour(){
    const Http = new XMLHttpRequest()
    const url='/a'
    Http.open("GET", url)
    Http.send()
    Http.onreadystatechange=(e)=>{
    var resp = JSON.parse(Http.responseText)
    console.log(resp)
    if(resp.number.len<3){
        resp.number = '0' + resp.number
        if(resp.number.len<3){
            resp.number = '0' + resp.number
        }
    }
    var node = document.createElement("H2")
    var textnode = document.createTextNode("Number #" + resp.number + ": " + resp.name)
    node.appendChild(textnode)
    document.body.appendChild(node)
    var node = document.createElement("IMG")
    node.setAttribute('src', resp.card)
    document.body.appendChild(node)
    return false
}}