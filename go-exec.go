package main

import (
	"bytes"
	"context"
	"crypto/md5"
	"crypto/tls"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"time"
)

type ResponseItem struct {
	ID      int    `json:"id"`
	Comando string `json:"comando"`
	Hash    string `json:"hash"`
	Timeout int    `json:"timeout"`
	Bash    bool   `json:"bash"`
	Process bool   `json:"process"`
}

type Message struct {
	Status string `json:"status"`
}

type Config struct {
	AuthKey string `json:"auth_key"`
}

var debug bool = true
var loop_sec time.Duration = 10
var api_url string = "http://127.0.0.1:5000/api/v1.0/"
var md5_shuffles string = "shablau123"
var auth_key string = ""

func main() {
	rand.Seed(time.Now().UnixNano())

	// check config file
	load_config()

	// infinite loop
	for {
		// get the current time before executing the command - for duration calculation
		startCheck := time.Now()
		// check the API
		if debug {
			log.Println("checking API...")
		}
		apiCheck()
		// next check in var loop_sec seconds
		endCheck := time.Since(startCheck)
		if endCheck < loop_sec*time.Second {
			time.Sleep(loop_sec*time.Second - endCheck)
		}
	}
}

func load_config() {
	// check if the config file exists
	if _, err := os.Stat("go-exec.json"); os.IsNotExist(err) {
		// if the file does not exist, create a new one with default settings
		config := Config{AuthKey: generateRandomString(50)}
		configJson, err := json.MarshalIndent(config, "", "  ")
		if err != nil {
			log.Println("Erro ao criar configuração padrão:", err)
			return
		}
		err = ioutil.WriteFile("go-exec.json", configJson, 0644)
		if err != nil {
			log.Println("Erro ao gravar configuração padrão no arquivo:", err)
			return
		}
		log.Println("Arquivo de configuração criado com sucesso.")
	}
	// if the file exists, read the settings
	configJson, err := ioutil.ReadFile("go-exec.json")
	if err != nil {
		log.Println("Erro ao ler arquivo de configuração:", err)
		return
	}
	var config Config
	err = json.Unmarshal(configJson, &config)
	if err != nil {
		log.Println("Erro ao decodificar configuração:", err)
		return
	}
	log.Println("Configuração lida com sucesso!")
	auth_key = config.AuthKey
}

func generateRandomString(length int) string {
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	result := make([]byte, length)
	for i := range result {
		result[i] = letters[rand.Intn(len(letters))]
	}
	return string(result)
}

func connect_http(url string, method string, content_type string, postData string) (*http.Response, error) {
	// configure client HTTP to use TLS transport and ignore certificate verification -- just for testing
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr, Timeout: time.Duration(10 * time.Second)}

	// create a POST request body
	reqBody := bytes.NewBufferString(postData)

	// create a POST request to the API URL
	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		//panic(err)
		log.Println("ERROR! Create request failed!")
		return nil, err
	}

	req.Header.Set("Content-Type", content_type)
	resp, err := client.Do(req)
	if err != nil {
		//panic(err)
		log.Println("ERROR! Request failed!")
		return nil, err
	}
	//defer resp.Body.Close()

	// check if the response is a 200 OK
	if resp.StatusCode != http.StatusOK {
		log.Printf("ERRO! Status da resposta: %v\n", resp.Status)
		return nil, err
	}
	// if ok, return the response
	return resp, nil
}

func apiCheck() {

	// get hostname
	hostname, err := os.Hostname()
	if err != nil {
		panic(err)
	}
	// connect to http and return the response
	postData := fmt.Sprintf("hostname=%s&auth_key=%s", hostname, auth_key)
	resp, err := connect_http(api_url+"list_cmd", "POST", "application/x-www-form-urlencoded", postData)
	if resp == nil {
		log.Println("ERROR! Connect HTTP failed!")
		return
	}
	if err != nil {
		log.Printf("ERROR! Connect HTTP failed! %v\n", err)
		return
	}
	defer resp.Body.Close()

	// decode the response body into a list of items
	var responseItems []ResponseItem
	if err := json.NewDecoder(resp.Body).Decode(&responseItems); err != nil {
		//panic(err)
		log.Printf("ERROR! Decode failed! %v\n", err)
		return
	}

	if debug {
		log.Printf("Status da resposta: %v\n", resp.Status)
		log.Println("--------")
	}

	// loop through the items and print them
	for _, item := range responseItems {
		log.Printf("ID: %d\n", item.ID)

		// get the command by ID
		cmd_id := item.ID
		log.Printf("cmd_id: %v", cmd_id)
		apiCmdGet(cmd_id)

		log.Println("----------------------------------")
	}
}

func apiCmdGet(cmd_id int) {

	// get hostname
	hostname, err := os.Hostname()
	if err != nil {
		panic(err)
	}
	// connect to http and return the response
	postData := fmt.Sprintf("hostname=%s&auth_key=%s&cmd_id=%v", hostname, auth_key, cmd_id)
	resp, err := connect_http(api_url+"get_cmd", "POST", "application/x-www-form-urlencoded", postData)
	if resp == nil {
		log.Println("ERROR! Connect HTTP failed!")
		return
	}
	if err != nil {
		log.Printf("ERROR! Connect HTTP failed! %v\n", err)
		return
	}
	defer resp.Body.Close()

	// decode the response body into a list of items
	var responseItems []ResponseItem
	if err := json.NewDecoder(resp.Body).Decode(&responseItems); err != nil {
		//panic(err)
		log.Println("ERROR! Decode failed!")
		return
	}

	if debug {
		log.Printf("Status da resposta: %v\n", resp.Status)
		log.Println("--------")
	}

	// loop through the items and print them
	for _, item := range responseItems {
		log.Printf("ID: %d, Comando: %s, Hash: %s, Timeout: %v, Bash: %v, Process: %v \n", item.ID, item.Comando, item.Hash, item.Timeout, item.Bash, item.Process)

		cmd_id := item.ID
		cmd_input := item.Comando
		cmd_hash := item.Hash
		cmd_timeout := time.Duration(item.Timeout)
		cmd_bash := false
		cmd_bash = item.Bash
		cmd_process := false
		cmd_process = item.Process

		// check if the md5 hash of the string is valid
		// shablau123 is the string that shuffles the md5 hash
		input_encoded := cmd_input + md5_shuffles
		input_md5 := md5.Sum([]byte(input_encoded))
		expectedHash := hex.EncodeToString(input_md5[:])

		if cmd_hash == expectedHash {
			log.Println("A hash é válida, executando comando...")
			// check if the command is a process or a bash command
			if cmd_process {
				// get the current time before executing the command - for duration calculation
				startTime := time.Now()

				cmd := exec.Command(cmd_input)
				cmd.Stdout = os.Stdout
				err := cmd.Start()
				if err != nil {
					log.Fatal(err)
				}
				cmd_stdout := cmd.Process.Pid
				cmd_stderr := err
				cmd_exitCode := cmd.ProcessState.ExitCode()
				log.Printf("stdout:  %d\n", cmd_stdout)
				log.Printf("stderr: %v\n", cmd_stderr)
				log.Printf("exit code: %d\n", cmd_exitCode)

				// get the current time after executing the command - calculate the duration
				cmd_duration := time.Since(startTime)
				log.Printf("duration: %v\n", cmd_duration)

				// post the result to the API
				apiCmdResult(cmd_id, cmd_stdout, cmd_stderr, cmd_exitCode, cmd_duration)

			} else {
				// get the current time before executing the command - for duration calculation
				startTime := time.Now()

				var cmd *exec.Cmd
				ctx, cancel := context.WithTimeout(context.Background(), cmd_timeout*time.Second)
				defer cancel()

				if cmd_bash {
					cmd = exec.CommandContext(ctx, "bash", "-c", cmd_input)
				} else {
					// split the string into a list of arguments - the first argument is the command
					parts := strings.Split(cmd_input, " ")
					cmd = exec.CommandContext(ctx, parts[0], parts[1:]...)
				}
				out, err := cmd.CombinedOutput()
				cmd_stdout := string(out)
				cmd_stderr := err
				cmd_exitCode := cmd.ProcessState.ExitCode()
				log.Printf("stdout: %v\n", cmd_stdout)
				log.Printf("stderr: %v\n", cmd_stderr)
				log.Printf("exit code: %d\n", cmd_exitCode)

				// get the current time after executing the command - calculate the duration
				cmd_duration := time.Since(startTime)
				log.Printf("duration: %v\n", cmd_duration)

				// post the result to the API
				apiCmdResult(cmd_id, cmd_stdout, cmd_stderr, cmd_exitCode, cmd_duration)
			}

		} else {
			log.Println("A hash é inválida, ignorando comando!")
		}
	}
}

func apiCmdResult(cmd_id int, cmd_stdout interface{}, cmd_stderr interface{}, cmd_exitCode int, cmd_duration time.Duration) {

	// get hostname
	hostname, err := os.Hostname()
	if err != nil {
		panic(err)
	}
	// connect to http and return the response
	postData := fmt.Sprintf("hostname=%s&auth_key=%s&cmd_id=%d&cmd_stdout=%v&cmd_stderr=%v&cmd_exitCode=%d&cmd_duration=%v", hostname, auth_key, cmd_id, cmd_stdout, cmd_stderr, cmd_exitCode, cmd_duration)
	// connect to http and return the response
	resp, err := connect_http(api_url+"cmd_result", "POST", "application/x-www-form-urlencoded", postData)
	if resp == nil {
		log.Println("ERROR! Connect HTTP failed!")
		return
	}
	if err != nil {
		log.Printf("ERROR! Connect HTTP failed! %v\n", err)
		return
	}
	defer resp.Body.Close()

	var message []Message
	err = json.NewDecoder(resp.Body).Decode(&message)
	if err != nil {
		log.Printf("Erro ao decodificar resposta: %v\n", err)
		return
	}
	for _, item := range message {
		log.Printf("Retorno: %v\n", item.Status)
	}
}
