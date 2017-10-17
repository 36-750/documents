(ns week8t.core
  (:require [clojure.future :refer :all])
  (:gen-class))

(defn sum
  "Sum a list of numbers"
  [numbers]
  (reduce + 0 numbers))

(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (print "Activities done: ")
  (let [activities '[sum]]
    (doseq [activity activities]
        (print (name activity) " ")))
  (println ""))
