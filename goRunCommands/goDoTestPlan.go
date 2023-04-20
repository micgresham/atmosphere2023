package main

import (
	"bytes"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"strings"
	"syscall"
	"time"

	"golang.org/x/crypto/ssh"
	"golang.org/x/term"
	"sigs.k8s.io/yaml"
)

var appName = "GoDoTestPlan"
var appVer = "1.0"
var appAuthor = "Sarah Tovar"
var appAuthorEmail = "sarah.tovar@hpe.com"
var pgmDescription = fmt.Sprintf("%s: Program to grab files for test plan.", appName)

type Switch struct {
	Name  string `yaml:"name"`
	Ip    string `yaml:"ip"`
	Group string `yaml:"group"`
	Site  string `yaml:"site"`
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func createDirectory(directoryName string) {
	if _, err := os.Stat(directoryName); errors.Is(err, os.ErrNotExist) {
		err := os.Mkdir(directoryName, os.ModePerm)
		if err != nil {
			log.Println(err)
		}
	}
}

func IsDirEmpty(name string) (bool, error) {
	f, err := os.Open(name)
	if err != nil {
		return false, err
	}
	defer f.Close()

	// read in ONLY one file
	_, err = f.Readdir(1)

	// and if the file is EOF... well, the dir is empty.
	if err == io.EOF {
		return true, nil
	}
	return false, err
}

func main() {
	fmt.Println("-------------------------------------")
	fmt.Printf("%s Version: %s\r\n", appName, appVer)
	fmt.Printf("Author: %s (%s)\r\n", appAuthor, appAuthorEmail)
	fmt.Println("-------------------------------------")

	// Open file
	switchFile, err := ioutil.ReadFile("inputs/switch_list.yml")
	if err != nil {
		log.Fatal(err)
	}
	// Get the list of switches
	switches := make(map[string]Switch)
	error2 := yaml.Unmarshal(switchFile, &switches)
	if error2 != nil {
		log.Fatal(error2)
	}
	//fmt.Println(switches)
	// Open file
	commandFile, err := ioutil.ReadFile("inputs/commands.yml")
	if err != nil {
		log.Fatal(err)
	}
	// Get the list of Commands
	commands := make(map[string][]string)
	//fmt.Println(commands)
	error3 := yaml.Unmarshal(commandFile, &commands)
	if error3 != nil {
		log.Fatal(error3)
	}

	// Get username, collection type, and password from user
	fmt.Print("Enter Username: ")
	var username string
	fmt.Scanln(&username)

	fmt.Print("Enter Password: ")
	bytepw, err := term.ReadPassword(int(syscall.Stdin))
	if err != nil {
		log.Fatal(err)
	}
	password := string(bytepw)

	fmt.Println("")
	fmt.Print("Pre or Post: ")
	var collectiontype string
	fmt.Scanln(&collectiontype)

	fmt.Printf("\nUsername: %s --  Password: %s -- CollectionType: %s\n", username, password, collectiontype)

	// create directories
	fmt.Println("")
	fmt.Println("----------------------------------------------------------------------")
	fmt.Println("Making sure output directories exist and archiving any existing data")
	fmt.Println("----------------------------------------------------------------------")
	path := "outputs"
	archivePath := "outputs/archive"
	createDirectory(path)
	createDirectory(archivePath)
	currentTime := time.Now().Unix()
	stringTime := strconv.FormatInt(currentTime, 10)
	for _, s := range switches {
		siteOutputPath := path + "/" + s.Site
		siteArchivePath := path + "/archive/" + s.Site
		createDirectory(siteOutputPath)
		createDirectory(siteArchivePath)
		outputPath := path + "/" + s.Site + "/" + s.Name + "-" + strings.ToUpper(collectiontype)
		newPath := siteArchivePath + "/" + s.Name + "-" + strings.ToUpper(collectiontype) + stringTime
		fmt.Println(outputPath)
		empty, err := IsDirEmpty(outputPath)
		if err != nil {
			fmt.Println(err)
		}
		if empty == false {
			os.Rename(outputPath, newPath)
		}
		createDirectory(outputPath)
	}

	for _, s := range switches {
		fmt.Println("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		fmt.Println("DOING " + s.Name)
		// SSH client config
		config := &ssh.ClientConfig{
			User: username,
			Auth: []ssh.AuthMethod{
				ssh.Password(password),
			},
			HostKeyCallback: ssh.InsecureIgnoreHostKey(),
		}
		// using RequestPty works better and requires modes to be set
		modes := ssh.TerminalModes{
			ssh.ECHO:          0,     // disable echoing
			ssh.TTY_OP_ISPEED: 14400, // input speed = 14.4kbaud
			ssh.TTY_OP_OSPEED: 14400, // output speed = 14.4kbaud
		}

		// Connection to switch
		client, err := ssh.Dial("tcp", s.Ip+":22", config)
		if err != nil {
			log.Fatal(err)
		}
		defer client.Close()

		// Create sesssion
		sess, err := client.NewSession()
		if err != nil {
			log.Fatal("Failed to create session: ", err)
		}
		defer sess.Close()

		if err := sess.RequestPty("xterm", 40, 80, modes); err != nil {
			log.Fatal("request for pseudo terminal failed: ", err)
		}

		// create variable to store output from session
		var b bytes.Buffer
		sess.Stdout = &b

		// Start remote shell
		err = sess.Shell()
		if err != nil {
			log.Fatal(err)
		}
		for key, value := range commands {
			//fmt.Println(value)
			// Create new sesssion
			newSess, err := client.NewSession()
			if err != nil {
				log.Fatal("Failed to create session: ", err)
			}
			defer newSess.Close()
			if err := newSess.RequestPty("xterm", 40, 80, modes); err != nil {
				log.Fatal("request for pseudo terminal failed: ", err)
			}
			// StdinPipe for commands
			stdin, err := newSess.StdinPipe()
			if err != nil {
				log.Fatal(err)
			}
			// create variable to store output from session
			var b bytes.Buffer
			newSess.Stdout = &b

			// Start remote shell
			err = newSess.Shell()
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println("-----------------")
			fmt.Println(key)
			if key == "router" {
				if s.Group == "router" {
					fmt.Println("This is a router")
					for _, v := range value {
						fmt.Println("                                  " + v)
						//time.Sleep(1 * time.Second)
						// if the string starts with sleep then sleep for 15 seconds else run the command
						if strings.HasPrefix(v, "sleep") {
							time.Sleep(15 * time.Second)
						} else {
							_, err = fmt.Fprintf(stdin, "%s\n", v)
							if err != nil {
								log.Fatal(err)
							}
							time.Sleep(1 * time.Second)
						}
					}
					fmt.Println("Writing router Data to File")
					time.Sleep(5 * time.Second)
					savePath := (path + "/" + s.Site + "/" + s.Name + "-" + strings.ToUpper(collectiontype) + "/" + key + ".txt")
					// Create file for output
					f, err := os.Create(savePath)
					check(err)
					defer f.Close()

					// Save output to file created
					_, err = b.WriteTo(f)
					time.Sleep(1 * time.Second)
				} else {
					fmt.Println("This is NOT a router do not do special Router commands")
				}
			} else {
				fmt.Println("Running " + key + " Commands")
				for _, v := range value {
					fmt.Println("                                  " + v)
					//time.Sleep(1 * time.Second)
					// if the string starts with sleep then sleep for 15 seconds else run the command
					if strings.HasPrefix(v, "sleep") {
						time.Sleep(15 * time.Second)
					} else {
						_, err = fmt.Fprintf(stdin, "%s\n", v)
						if err != nil {
							log.Fatal(err)
						}
						time.Sleep(1 * time.Second)
					}
				}
				fmt.Println("Writing " + key + " to File")
				time.Sleep(5 * time.Second)
				savePath := (path + "/" + s.Site + "/" + s.Name + "-" + strings.ToUpper(collectiontype) + "/" + key + ".txt")
				// Create file for output
				f, err := os.Create(savePath)
				check(err)
				defer f.Close()
				// Save output to file created
				_, err = b.WriteTo(f)
				time.Sleep(1 * time.Second)
			}
		}
	}
}
