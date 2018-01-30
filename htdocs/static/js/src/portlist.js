define(function(require) {

    var DataTables = require('libs/datatables.min');
    var moduleSort = require('dt_plugins/modulesort');
    var URI = require('libs/urijs/URI');
    var Moment = require('moment');
    var SparkLine = require('');

    var selectors = {
        table: '#portlist-table',
        ifclassfilter: '#ifclassfilter',
        queryfilter: '#queryfilter',
        filterForm: '#filters'
    }


    /*
     * dtColumns defines the data we want to use from the result set from the
     * api. They are in order of appearance in the table - changes here may need
     * changes in the template aswell.
     *
     * More information about the options for each column can be seen at
     * https://datatables.net/reference/option/ -> columns
     */
    var dtColumns = [
        {
            name: 'portadmin-link',
            render: function(data, type, row, meta) {
                if (isSwPort(row)) {
                    return '<a href="' + NAV.urls.portadmin_index + row.id + '" title="Configure port in Portadmin"><img src="/static/images/toolbox/portadmin.svg" style="height: 1em; width: 1em" /></a>';
                }
                return '';
            },
            orderable: false
        },

        {
            data: "netbox.sysname"
            name: 'netbox',
        },

        {
            data: "ifname",
            name: 'ifname',
            type: "module",
            render: function(data, type, row, meta) {
                return '<a href="' + row.object_url + '">' + data + '</a>';
            }
        },

        {
            data: "ifalias",
            name: 'ifalias',
            render: function(data, type, row, meta) {
                return '<a href="' + row.object_url + '">' + data + '</a>';
            }
        },

        {
            data: 'module',
            name: 'module',
            render: function(data, type, row, meta) {
                return data
                     ? '<a href="' + data.object_url + '">' + data.name + '</a>'
                     : '';
            }
        },

        {
            data: "ifadminstatus",
            name: 'adminstatus',
            type: "statuslight",
            render: renderStatus
        },

        {
            data: "ifoperstatus",
            name: 'operstatus',
            type: "statuslight",
            render: renderStatus
        },

        {
            data: "vlan",
            name: 'vlan',
            render: function(data, type, row, meta) {
                if (row['trunk']) {
                    return "<span title='Trunk' style='border: 3px double black; padding: 0 5px'>" + data + "</span>"
                }
                return data;
            }
        },

        {
            data: "speed",
            name: 'speed',
            render: function(data, type, row, meta) {
                if (row.duplex === 'h') {
                    return data + '<span class="label warning" title="Half duplex" style="margin-left: .3rem">HD</span>';
                }
                return row.speed ? data : "";
            }
        },

        {
            data: 'to_netbox',
            name: 'to-netbox',
            render: function(data, type, row, meta) {
                return data
                     ? '<a href="' + data.object_url + '">' + data.sysname + '</a>'
                     : '';
            }
        },

        {
            data: 'to_interface',
            name: 'to-interface',
            render: function(data, type, row, meta) {
                return data
                     ? '<a href="' + data.object_url + '">' + data.ifname + '</a>'
                     : '';
            }
        },

        {
            data: null,
            name: 'traffic-sparkline',
            render: function(data, type, row, meta) {
                return "Fake";
            }
        },

    ];


    /** Renders a light indicating status (red or green) */
    function renderStatus(data, type, row, meta) {
        var color = data === 2 ? 'red' : 'green';
        return '<img src="/static/images/lys/' + color + '.png">';
    }

    /* Returns if this is a swport or not */
    function isSwPort(row) {
        return row.baseport !== null;
    }


    /** TABLE INITIATION */

    function PortList() {
        console.log('creating table');
        var table = createTable();
        renderColumnSwitchers(table);
        addColumnSwitcherListener(table);
        reloadOnChange(table);
    }

    function renderColumnSwitchers(table) {
        var $container = $('#column-switchers');
        dtColumns.forEach(function(column, index) {
            var $switcher = $('<li data-name="' + index + '">' + index + '</li>');
            $container.append($switcher);
        });
        $container.on('click', function(e) {
            var index = $container.find('li').index(e.target);
            var column = table.column(index);
            column.visible(!column.visible());
        })
    }


    function addColumnSwitcherListener(table) {
        // column: index of column
        // state: false if hidden, true if shown
        table.on('column-visibility.dt', function(e, settings, column, state) {
            console.log("visibility changed");
            console.log(settings);
            console.log(column);
            console.log(state);
        })
    }

    function reloadOnChange(table) {
        // Reload at most every reloadInterval ms
        var reloadInterval = 500  // ms
        var throttled = _.throttle(reload.bind(this, table), reloadInterval, {leading: false});
        $(selectors.filterForm).on('change keyup', throttled);
    }

    function reload(table) {
        table.ajax.url(getUrl()).load();
    }

    function createTable() {
        return $(selectors.table).DataTable({
            autoWidth: false,
            paging: true,
            pagingType: 'simple',
            orderClasses: false,
            ajax: {
                url: getUrl(),
                dataFilter: translateData
            },
            columns: dtColumns,
            order: [[1, 'asc']],
            dom: "<><'#infoprocessing'ir>t<p>",
            language: {
                info: "_TOTAL_ entries",
                processing: "Loading...",
            }
        });
    }

    /**
     * Translate data keys from response to something datatables understand
     */
    function translateData(data) {
        var json = jQuery.parseJSON( data );
        json.recordsTotal = json.count;
        json.data = json.results;
        return JSON.stringify( json );
    }

    function getUrl() {
        var baseUri = URI("/api/1/interface/");
        var uri = addFilterParameters(baseUri);
        return uri.toString();
    }


    /** FILTER STUFF */


    /* Create url based on filter functions. Each filter is responsible for
    creating a parameter and value */
    function addFilterParameters(uri) {
        filters = [netboxFilter, ifClassFilter, queryFilter];
        uri.addSearch(filters.reduce(function(obj, func) {
            return Object.assign(obj, func());
        }, {}));
        console.log(uri.toString());
        return uri;
    }

    function netboxFilter() {
        return {};
    }

    function ifClassFilter() {
        return { ifclass: $(selectors.ifclassfilter).val() }
    }

    function queryFilter() {
        return { search: $(selectors.queryfilter).val() }
    }

    return PortList

});