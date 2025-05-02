

  <div class="image">
    <!-- <img src="https://github.com/DiogoFerrari/tidypolars4sci/blob/master/docs/tidypolars4sci.png?raw=True" alt="Description" style="max-width: 500px; margin-left: 10px"> -->
    <!-- <img src="./tidypolars4sci.png" alt="Description" style="max-width: 1000px; margin-left: 0px"> -->
	<!-- NOTE: style="max-width: 100%; height: auto;"  makes the image auto-shrink for smartphones-->
    <img src="./_css/tidypolars4sci.png" alt="Description" style="max-width: 100%; height: auto;">

  </div>
  
  
<h1 style="text-align:center">Combining Polars and Tidyverse for Python</h1>
<div align="center">
  <!-- <a href="https://docs.rs/polars/latest/polars/"> -->
  <!--   <img src="https://docs.rs/polars/badge.svg" alt="Rust docs latest"/> -->
  <!-- </a> -->
  <!-- <a href="https://crates.io/crates/polars"> -->
  <!--   <img src="https://img.shields.io/crates/v/polars.svg" alt="Rust crates Latest Release"/> -->
  <!-- </a> -->
  <a href="https://pypi.org/project/tidypolars4sci/">
    <img src="https://img.shields.io/pypi/v/tidypolars4sci.svg" alt="PyPI Latest Release"/>
  </a>
  
  
  <!-- <a href="https://app.netlify.com/sites/diogoferrari/deploys"> -->
  <!--   <img src="https://api.netlify.com/api/v1/badges/92e92c9d-e001-43c4-b925-daae5b320996/deploy-status"/> -->
  <!-- </a> -->
  
  <!-- <a href="https://doi.org/10.5281/zenodo.7697217"> -->
  <!--   <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.7697217.svg" alt="DOI Latest Release"/> -->
  <!-- </a> -->
</div>


 <!-- dprint-ignore-start -->
!!! info "Note" 
    <center>This site is still under construction, but full documentation can be found in package docstrings and [API Reference](api.md).</center>
<!-- dprint-ignore-end -->


<!-- # TidyPolars $^{4sci}$ -->

<!-- <div class="two-column"> -->
<!--   <div class="text"> -->
<!--     <p> -->
<!-- <b>tidypolars4sci</b> provides functions that match as closely as possible to R's <a href="https://www.tidyverse.org/">Tidyverse</a> functions for manipulating data frames and conducting data analysis in Python using the blazingly fast <a href="https://github.com/pola-rs/polars">Polars</a> as backend.</p> -->
<!-- <p>The name <strong>tidypolars4sci</strong> reflects the module's main features:</p> -->
<!-- <ol> -->
<!--     <li>Matches the function names and functionalities of R's <a href="https://tidyverse.org/">Tidyverse</a>.</li> -->
<!--     <li>Leverages the performance and efficiency of <a href="https://github.com/pola-rs/polars">Polars</a> under the hood.</li> -->
<!--     <li>Tailored for scientific research, extending the default functionalities of both Polars and Tidyverse.</li> -->
<!-- </ol> -->
<!-- 	</p> -->
<!--   </div> -->
<!--   <div class="image"> -->
<!--     <img src="https://github.com/DiogoFerrari/tidypolars4sci/blob/master/docs/tidypolars4sci.png?raw=True" alt="Description" style="max-width: 500px; margin-left: 10px"> -->
<!--   </div> -->
<!-- </div> -->


**tidypolars$^{4sci}$** provides functions that match as closely as possible to R's [Tidyverse](https://www.tidyverse.org/) functions for manipulating data frames and conducting data analysis in Python using the blazingly fast [Polars](https://github.com/pola-rs/polars) as backend.

# Key features

<!-- - **Fast**: Uses [Polars](https://docs.pola.rs/) as backend for data manipulation. So it inherits many advantages of Polars: fast, parallel, GPU support, etc. -->
<!-- - **Tidy**: Keeps the data in tidy (rectangular table) format (no multi-indexes) -->
<!-- - **Syntax**: While Polars is fast, the syntax is not the most intuitive. The package provides frontend methods that match R's [Tidyverse](https://www.tidyverse.org/) functions, making it easier for users familiar with that ecosystem to transition to this library. -->
<!-- - **Extended functinalities**: Polars is extended to facilitate data manipulation and analysis for academic research. -->
<!-- - **Research**: The package is designed to facilitate academic research, data analysis, and reporting of the results. It provides functions to quickly produce tables using minimal code, and whose output matches the format commonly used in academic publications. Those output formats include LaTeX, Excel, CSV, and others. -->


- **Fast**: Uses [Polars](https://docs.pola.rs/) as a backend for data manipulation. Therefore, it inherits many advantages of that module: fast, parallel, GPU support, etc.
- **Tidy**: Keeps the data in a tidy (rectangular table) format (no multi-indexes).
- **Syntax**: While Polars is fast, the syntax is not the most intuitive. The package provides frontend methods that match R's [Tidyverse](https://www.tidyverse.org/) functions, making it easier for users familiar with that ecosystem to transition to this library.
- **Extended functionalities**: Polars is extended to facilitate data manipulation and analysis for academic research.
- **Research**: The package is designed to facilitate academic research, data analysis, and reporting of results. It provides functions to quickly produce tables using minimal code, and whose output matches the format commonly used in academic publications. Those output formats include LaTeX, Excel, CSV, and others.


<!-- ## Details -->

<!-- **tidypolars$^{4sci}$** is an **extended** API for [Polars](https://github.com/pola-rs/polars). One of the **main advantages** of using Polars as a data manipulation engine is its exceptional speed when compared to other alternatives (see [here](https://pola.rs/posts/benchmarks/)). -->

<!-- The primary distinction between **tidypolars$^{4sci}$** and Polars lies in user interaction. The frontend functions are designed to closely resemble those available in R's [Tidyverse](https://tidyverse.org/), making it easier for users familiar with that ecosystem to transition to this library. -->

<!-- Another useful feature of **tidypolars$^{4sci}$** is its extensive functionality aimed at facilitating data analysis and reporting for scientific research and academic publications. This includes the creation of LaTeX tables, which enhances the presentation of results. -->

<!-- ## Performance -->

# Syntax

The main motivation for **tidypolars$^{4sci}$** was to provide more readable and elegant syntax in Python for [Polars](https://docs.pola.rs/), similar to R's [Tidyverse](https://www.tidyverse.org/), while (1) extending Polars functionalities to facilitate data manipulation and (2) keeping the advantages of speed and efficiency in data processing provided by that module. Here are some examples of syntax differences:

=== "tidypolars4sci"
    ```python
	tab = (df
		   .filter(tp.col("carb")<8)
		   .filter(tp.col("name").str.contains("Mazda|Toyota|Merc"))
		   .mutate(cyl_squared = tp.col("cyl")**2,
				   cyl_group = tp.case_when(tp.col("cyl")<tp.col("cyl").mean(), "Low cyl",
 											tp.col("cyl")>tp.col("cyl").mean(), "High cyl",
											True, 'Average cyl'),
                   am = tp.as_factor("am")
				   )
			.select("name", "am")
			.pivot_wider(values_from="name", names_from="am",
						 values_fn=tp.element().sort().str.concat("; "))
			)
    ``` 
=== "Tidyverse (R)"
    ```R
    tab = (df
        %>% filter(carb < 8)
        %>% filter(str_detect(name, "Mazda|Toyota|Merc"))
        %>% mutate(cyl_squared = cyl^2,
                   cyl_group = case_when(cyl < mean(cyl) ~ "Low cyl",
                                         cyl > mean(cyl) ~ "High cyl",
                                         TRUE ~ "Average cyl"),
                   am = as.factor(am)
				   )
        %>% select(name, am)
        %>% pivot_wider(names_from = am, values_from = name,
                        values_fn = list(name = ~ paste(sort(.), collapse = "; ")))
    )
    ``` 
=== "Polars"
    ```python
    tab = (df.to_polars()
           .filter(pl.col("carb") < 8)
           .filter(pl.col("name").str.contains("Mazda|Toyota|Merc"))
           .with_columns([
               (pl.col("cyl") ** 2).alias("cyl_squared"),
               (pl
                .when(pl.col("cyl") < pl.col("cyl").mean()).then(pl.lit("Low cyl"))
                .when(pl.col("cyl") > pl.col("cyl").mean()).then(pl.lit("High cyl"))
                .otherwise(pl.lit("Average cyl")).alias("cyl_group")),
               (pl.col("am").cast(pl.String).cast(pl.Categorical).alias("am"))
           ])
           .select(["name", "am"])
           .with_columns(idx=0)
           # pivot-wide
           .pivot(index='idx', on="am", values="name",
                  aggregate_function=pl.element().sort().str.concat("; ")
                  )
           .drop('idx')
           )
    ``` 
=== "Pandas"
    ```python
     tab = (df
            .query(f"carb < 8")
            .query(f"name.str.contains('Mazda|Toyota|Merc')")
            .assign(cyl_squared = lambda col: col["cyl"]**2,
                    cyl_group = lambda col: pd.cut(col["cyl"], 
                                                   bins=[-float("inf"), col["cyl"].mean(),
												          float("inf")],
                                                   labels=["Low cyl", "High cyl"]),
                    am = lambda col: col["am"].astype("str"))
            .filter(["name", "am"])
            .pivot_table(columns="am", values="name",
                         aggfunc = lambda x: "; ".join(x)))
    ``` 







# Performance


In most cases, the performance of **tidypolars$^{4sci}$** is comparable to Polars. In some instances, it may operate slightly slower due to the additional functionalities provided by the module. Check the section [Performance](performance/overview.md) for details.

<!-- ## Similar projects -->

<!-- - [tidypolars](https://pypi.org/project/tidypolars/): tidypolars was the starting point of tidypolars4sci -->

