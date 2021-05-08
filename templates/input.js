const localVideo = document.querySelector('video');
var videoSelect = document.querySelector('select#video');
var audioSelect = document.querySelector('select#audio');
let localStream;
let constraint;

function getDevices(){
	return navigator.mediaDevices.enumerateDevices()
}

function gotDevices(devices){
	devices.forEach(function(device){
		if(device['kind'] == 'audioinput'){
			let opt = document.createElement('option');
			opt.value = device['deviceId'];
			opt.innerText = device['label'];
			audioSelect.appendChild(opt);
		}else if(device['kind'] == 'videoinput'){
			let opt = document.createElement('option');
			opt.value = device['deviceId'];
			opt.innerText = device['label'];
			videoSelect.appendChild(opt);
		}
	})
	changeConstraint();
}

function changeConstraint(){
	constraint = {video: {deviceId: videoSelect.value}, audio: {deviceId: audioSelect.value}};
	getMedia(constraint);
}

function gotLocalMediaStream(mediaStream) {
  localStream = mediaStream;
  localVideo.srcObject = mediaStream;
}

function getMedia(mediaStreamConstraints){
	// 这里是重点，必须要先停止才可以
	if(localStream){
		localStream.getVideoTracks()[0].stop();
	}
	navigator.mediaDevices.getUserMedia(mediaStreamConstraints)
	  .then(gotLocalMediaStream).catch(handleLocalMediaStreamError);
}

function handleLocalMediaStreamError(error) {
  console.log('navigator.getUserMedia error: ', error);
}

getDevices().then(gotDevices)

audioSelect.onchange=changeConstraint;
videoSelect.onchange=changeConstraint;
