(defproject week8t "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.8.0"]
                 [clojure-future-spec "1.9.0-alpha17"]
                 [org.clojure/test.check "0.9.0"]]
  :main ^:skip-aot week8t.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}})
