$(document).ready(function() { 
  $("#index-table").tablesorter({
    // default sortInitialOrder setting
    sortInitialOrder: "asc", 

    // tablesorter document 
    // https://mottie.github.io/tablesorter/docs/example-widget-filter.html
    // hidden filter input/selects will resize the columns, so try to minimize the change
    widthFixed : true,

    // initialize filter widgets
    widgets: ["filter"],

    ignoreCase: false,

    widgetOptions : {
      filter_columnFilters : true,
      filter_columnAnyMatch: true,
      filter_filteredRow : 'filtered',
      filter_hideEmpty : true,
      filter_hideFilters : true,
      filter_ignoreCase : true,
      filter_liveSearch : true,
      filter_matchType : { 'input': 'exact', 'select': 'exact' },
      filter_onlyAvail : 'filter-onlyAvail',
      filter_placeholder : { search : '', select : '' },
      filter_searchDelay : 300,
      filter_searchFiltered: true,
      filter_serversideFiltering : false,
      filter_startsWith : false,
      filter_useParsedData : false,
      filter_defaultAttrib : 'data-value',
      filter_selectSourceSeparator : '|'
    },

    // pass the headers argument and passing a object
    headers: {
      2: { sorter: false, filter: false }
    }
  }); 
});
