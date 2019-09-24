# CHAIJIN WEB


## WORKER

* worker는 lockfile 모듈에 의존함.

### 작동시
1. JOB/job.lock 락파일을 생성
	1. 무한루프
		1. JOB/PID/$PID 파일을 생성. (루프 돌때마다 내용을 비워줌)
		1. lock을 걸고
			1. JOB/READY 에서 파일을 하나 선택
			1. JOB/DOING 으로 옮김
			1. JOB/PID/$PID 에 파일이름을 기록
		1. lock을 풀고
		1. 처리후 결과에 따라
			* JOB/OK 에 넣거나
			* JOB/FAIL 에 넣음
		
### ctrl+c 로 종료시
* JOB/PID/$PID 파일이 제거됨
  
### 비정상 종료시
* JOB/PID/$PID에 파일이름이 들어있다면, 해당 작업을 하다가 사망한 것
* 비이었다면, 놀다가 사망한 것 
  
### 재시도 대상 찾기
* JOB/DOING 에 있는 파일에 대해서
	* JOB/PID/$PID 파일에 이름이 없으면 
		* /JOB/READY로 이동
	* JOB/PID/$PID 파일에 이름이 있으면
		* $PID로 작동하는 worker가 없으면
			* /JOB/READY로 이동
			

