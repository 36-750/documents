(ns week8t.core-test
  (:require [clojure.test   :refer :all]
            [clojure.future :refer :all]
            [week8t.core    :refer :all]))

(deftest simple-sums
  (is (= (sum [1 2 3 4 5]) 15))
  (is (= (sum #{1 2 3 4 5}) 15))
  (is (= (sum []) 0))
  (is (= (sum [1]) 1)))


