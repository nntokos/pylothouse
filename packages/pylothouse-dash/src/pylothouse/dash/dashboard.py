import os

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dash_table
import plotly.graph_objs as go

'''
To use the dashboard:
1. Create a dashboard instance with dashboard = Dashboard('Dashboard Title')
2. Create pages with page = Page('Page Title', '/page-href')
3. Add page to dashboard dashboard.add_page(Page('Page Title', '/page-href'))
        The order of the components is the order that they will be added to the page
4. Create components with component = PageComponent('Component Title', body) or one of the class methods (table, plotly_figure, img, image_slider, etc.) (You can also directly use the add_<component>_component, methods of the page)
5. Add the components to the page with page.add_page_component(component) or directly page.add_graph_component, page.add_img_component, etc.
6. Run the dashboard
'''


def paths_relative_to_assets_folder(paths):
    '''
    Convert the given paths to be relative to the assets folder.
    If the paths are already relative to the assets folder, they will not be changed.
    If the paths are not relative to the assets folder, the function will try to find the assets folder in the path and keep the rest of the path.
    IF the assets folder is not found in the path, the function will add the assets folder to the beginning of the path.
    Therefore each path will be relative to the assets folder.

    Parameters:
    paths: list, the paths to be converted

    Returns:
    relative_paths: list, the paths relative to the assets folder
    '''
    relative_paths = []
    for path in paths:
        if not path.startswith('/assets'):
            if '/assets' in path:
                path = path[path.index('/assets'):]
            else:
                path = os.path.join('/assets', path)
        relative_paths.append(path)
    return relative_paths


class PageComponent:
    def __init__(self, title, id, body, show_title=True):
        '''
        Create a page component with the given title and body
        The component will be added to the given page at the moment of its initialization.
        A component cannot exists without a related parent page.

        Arguments:
        :param title: str, the title of the component
        :type title: str
        :param body: html.Div, the body of the component
        :type body: html.Div, dcc.Graph, dcc.Table, html.Img, etc.
        :param show_title: bool, whether to show the title of the component (default: True)
        :type show_title: bool

        Returns:
        :return: PageComponent, the page component with the given title and body

        '''
        self.id = id
        self.title = title
        self.child = body
        self.show_title = show_title
        self._callback_store = []
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, page):
        if not isinstance(page, Page):
            raise TypeError("The parent should be of type Page")
        # If the component's parent still has this component, remove it from the parent. Then set the new parent
        if self._parent is not None:
            if page == self._parent:
                return
            self._parent.remove_component(self)
        self._parent = page

        # If the component is not in the children of the parent, add it
        if page is not None and self not in page.children:
            page.add_component(self)


    def register_callbacks(self, app: dash.Dash):
        for callback in self._callback_store:
            app.callback(
                    callback['outputs'],
                    callback['inputs'],
                    prevent_initial_call=callback['prevent_initial_call']
                )(callback['function'])

    def layout(self):
        divs = []

        # Title
        if self.show_title:
            divs.append(html.H4(self.title, style={'text-align': 'center'}))

        # Body
        divs.append(self.child)

        return html.Div(divs, id=self.id)

    @classmethod
    def table(cls, title, id, data, show_title=True):
        '''
        Create a table with the given id and data

        Parameters:
        id: str, the id of the table
        data: list, the data of the table ["column1": [data1], "column2": [data2], ...]

        Returns:
        table: dash_table.DataTable, the table with the given id and data
        '''
        table = dash_table.DataTable(id=f'{id}-table', columns=[{"name": i, "id": i} for i in data.columns],
                                     data=data.to_dict('records'))
        return cls(title=title, id=id, body=table, show_title=show_title)

    @classmethod
    def plotly_figure(cls, title, id, figure, show_title=True):
        '''
        Create a graph with the given id and figure

        Parameters:
        id: str, the id of the graph
        figure: dict, the figure of the graph (Pass the go.Scatter object)

        Returns:
        graph: dcc.Graph, the graph with the given id and figure
        '''
        graph = html.Div([dcc.Graph(id=f'{id}-figure', figure=figure)],
                         style={'minHeight': '600px', 'borderBottom': '2px solid black'})
        return cls(title=title, id=id, body=graph, show_title=show_title)

    @classmethod
    def img(cls, title, id, src, show_title=True):
        '''
        Create an img with the given src. If the src is a local file, the path should be relative to the assets folder.
        This is automatically corrected in this function. However, if the src cannot have two '/assets' in the path.

        Parameters:
        src: str, the source of the image

        Returns:
        img: html.Img, the img with the given src
        '''
        src = paths_relative_to_assets_folder([src])[0]
        img = html.Img(src=src, id=f'{id}-img')
        return cls(title=title, id=id, body=img, show_title=show_title)

    @classmethod
    def image_slider(cls, title, id, images, show_title=True, captions=None):
        '''
        Create an image slider with the given id and images

        Parameters:
        id: str, the id of the image slider
        images: list, the images of the slider. If the images are local files, the paths should be relative to the assets folder
        title: str, the title of the slider (default: 'Image Slider')
        captions: list, the captions of the images (default: None). If None, the filenames of the images will be used as captions

        Returns:
        slider: dcc.Slider, the image slider with the given id and images
        '''
        images = paths_relative_to_assets_folder(images)
        if captions is None:
            captions = [os.path.basename(images[i]) for i in range(len(images))]
        title_div = html.H2(title)
        image_div = html.Img(id='image')
        slider_output = html.Div(id=f'{id}-slider-output-container')
        marks = {i: captions[i] if len(images) < 12 else '' for i in range(len(images))}
        slider = dcc.Slider(id=f'{id}-slider', min=0, max=len(images), value=0, marks=marks, step=None)
        slider_div = html.Div([slider], style={'width': '90%', 'margin': 'auto'})

        image_slider = html.Div([title_div, image_div, slider_output, slider_div], className="text-center",
                                style={'borderBottom': '2px solid black'})

        component = cls(title=title, id=id, body=image_slider, show_title=show_title)

        # @page.dashboard.app.callback(
        #     Output('slider-output-container', 'children'),
        #     Output('image', 'src'),
        #     [Input(id, 'value')]
        # )
        def update_output(value):
            return 'img: "{}"'.format(captions[value]), images[value]

        component._callback_store.append(
            {'outputs': [Output(f'{id}-slider-output-container', 'children'), Output(f'image-{id}', 'src')],
             'inputs': [Input({id}-slider, 'value')], 'function': update_output})

        return component
    
    # TODO: Add (Convenient all around solution) loading indicators
    @classmethod
    def update_component_button(cls, title, id, component_id, component_loader, loader_input=None, allow_duplicate=False, show_title=True, style=None):
        '''
        Create a button that updates a component with data loaded on demand.

        title: str, the title of the button component.
        id: str, the unique identifier for the button.
        component_id: str, the id of the component to update when the button is clicked.
        component_loader: function, the function to load data when the button is clicked.
        additional_inputs: list of dash.dependencies.Input or dash.dependencies.State, optional, additional inputs for the component_loader function.
        show_title: bool, optional, whether to show the title (default: True).
        style: dict, optional, the style parameters for the button (default: {'margin': '10px'}).

        Guidance for styling:
        - Use a dictionary to define CSS styles.
        - Example: {'margin': '10px', 'backgroundColor': 'blue', 'color': 'white'}.
        - Refer to Dash documentation for more styling options: https://dash.plotly.com/dash-html-components/button

        Returns:
        button: html.Button, the button with the given text
        '''
        if style is None:
            style = {'margin': '10px'}
        button = html.Button(title, id=f'{id}-button', n_clicks=0, className='btn btn-primary', style=style)
        btn_component = cls(title=title, id=id, body=button, show_title=show_title)
        
        def update_component_button_callback(n_clicks):
            if n_clicks > 0:
                args = []
                if loader_input:
                    for additional_input in loader_input:
                        args.append(additional_input)
                component = component_loader(*args)
                # btn_component.parent.remove_component(component_id)
                # btn_component.parent.add_component(component)
                return [component.layout()]
            return [dash.no_update]
        
        inputs = [Input(f'{id}-button', 'n_clicks')]
        
        btn_component._callback_store.append(
            {'outputs': [Output(component_id, 'children', allow_duplicate=allow_duplicate)], 'inputs': inputs, 'function': update_component_button_callback, 'prevent_initial_call': allow_duplicate})
        
        return btn_component

    @classmethod
    def action_button(cls, title, id, on_click, show_title=True, style=None):
        '''
        Creates an action button component with a callback function.

        Args:
            title (str): The title of the button.
            id (str): The unique identifier for the button.
            on_click (callable): The function to be called when the button is clicked.
            show_title (bool, optional): Whether to show the title. Defaults to True.
            style (dict, optional): CSS styles to apply to the button. Defaults to {'margin': '10px'}.

        Returns:
            component: An instance of the component with the action button and callback.

        The callback function `action_button_callback` is registered to handle the button's click events.
        It calls the provided `on_click` function when the button is clicked.
        '''
        if style is None:
            style = {'margin': '10px'}
        button = html.Button(title, id=id, n_clicks=0, className='btn btn-primary', style=style)
        component = cls(title=title, id=id, body=button, show_title=show_title)
        def action_button_callback(n_clicks):
            if n_clicks is None:
                return 'No clicks yet'
            on_click()
        component._callback_store.append(
            {'outputs': [], 'inputs': [Input(id, 'n_clicks')], 'function': action_button_callback})
        return component



class Page:
    """
    A class that represents a page in the dashboard

    :param title: Title of the page.
    :type title: str
    :param href: The href of the page.
    :type href: str
    :param children: The children of the page. These are divs. Usually added with the add_page_component method
    :type children: list
    :param dashboard: The dashboard that the page belongs to.
    :type dashboard: Dashboard
    :param layout: The layout of the page (default: 'SIMPLE_ONE_COLUMN')
    :type layout: str
    """

    def __init__(self, title, href, dashboard=None, children=None, subpages=None, layout='SIMPLE_ONE_COLUMN',
                 show_title: bool = True):
        self.title = title
        self.href = href
        self.page_id = '-'.join(href.split('/')[1:])

        # Children
        if children is None:
            children = []
        self._children = children
        for child in children:
            if isinstance(child, PageComponent):
                self._children.append(child.layout())
            else:
                raise TypeError(f"{self.__name__} Children should be of type PageComponent")

        # Subpages
        if subpages is None:
            subpages = []
        self.subpages = subpages
        for subpage in subpages:
            if isinstance(subpage, Page):
                self.subpages.append(subpage)
            else:
                raise TypeError(f"{self.__name__} Subpages should be of type Page")

        if dashboard is not None:
            if not isinstance(dashboard, Dashboard):
                raise TypeError(f"{self.__name__} dashboard should be of type Dashboard")
        self._dashboard = dashboard

        if not layout in ['SIMPLE_ONE_COLUMN']:
            raise ValueError("The layout should be one of the following: ['SIMPLE_ONE_COLUMN']")
        self._layout = layout

        self._show_title = show_title

    @property
    def children(self):
        return self._children

    @property
    def dashboard(self):
        return self._dashboard

    @dashboard.setter
    def dashboard(self, dashboard):
        # If the page's dashboard still has this page, remove it from the dashboard. Then set the new dashboard
        if self._dashboard is not None:
            if self._dashboard == dashboard:
                return
            self._dashboard.remove_page(self)
        self._dashboard = dashboard

        # If the page is not in the pages of the dashboard, add it
        if self not in dashboard.pages and dashboard is not None:
            dashboard.add_page(self)

    def register_callbacks(self, app):
        @app.callback(
            Output(f'page-content-{self.page_id}', 'children'),
            [Input('url', 'pathname')]
        )
        def display_page(pathname):
            if pathname == self.href:
                return self.layout()
            else:
                return html.Div()

        for child in self._children:
            if isinstance(child, PageComponent):
                child.register_callbacks(app)
        for subpage in self.subpages:
            subpage.register_callbacks(app)

    def layout(self):
        title = html.H1(self.title) if self._show_title else None
        sub_navbar = dbc.NavbarSimple(
            children=[dbc.NavItem(dbc.NavLink(subpage.title, href=subpage.href)) for subpage in self.subpages],
            brand=self.title,
            brand_href=self.href,
            color="dark",
            dark=True,
            className="p-2",  # Reduce padding to make it smaller
            style={"font-size": "14px", "height": "38px", "margin": "0px"},  # Reduce font size and height
            sticky="top",

        )
        main = html.Div(self._children)

        # TODO: Add more layouts.
        #  For now, only one column is supported, need something for a set of image and sliders for graphs
        if self._layout == 'SIMPLE_ONE_COLUMN':  # Default one column layout
            title = html.H1(self.title) if self._show_title else None
            sub_navbar = dbc.NavbarSimple(
                children=[dbc.NavItem(dbc.NavLink(subpage.title, href=subpage.href)) for subpage in self.subpages],
                brand=self.title,
                brand_href=self.href,
                color="dark",
                dark=True,
                className="p-2",  # Reduce padding to make it smaller
                style={"font-size": "14px", "height": "38px", "margin": "0px"},  # Reduce font size and height
                sticky="top",

            )
            main = html.Div([child.layout() for child in self._children])

        layout = html.Div([
            title,
            sub_navbar,
            main
        ])

        return layout    

    def fetch_component(self, component_id):
        return next((comp for comp in self._children if comp.id == component_id), None)

    def add_subpage(self, page):
        if not isinstance(page, Page):
            raise TypeError("The subpage should be of type Page")
        if page not in self.subpages:
            self.subpages.append(page)

    def add_component(self, component_or_id):
        if isinstance(component_or_id, PageComponent):
            component = component_or_id
        elif isinstance(component_or_id, str):
            component = next((comp for comp in self._children if comp.id == component_or_id), None)
            if component is None:
                raise ValueError(f"No component found with id: {component_or_id}")
        else:
            raise TypeError("Input should be either a PageComponent instance or a component id string")

        if component not in self._children:
            self._children.append(component)
        # Set the parent of the component to this page if it's not already set
        if component.parent is None or component.parent != self:
            component.parent = self

    def remove_component(self, component_or_id):
        '''
        AVOID USING THIS METHOD. NOT IMPLEMENTED WELL YET
        Remove a component from the page
        '''
        if isinstance(component_or_id, PageComponent):
            component = component_or_id
        elif isinstance(component_or_id, str):
            component = next((comp for comp in self._children if comp.id == component_or_id), None)
            if component is None:
                print(f"No component found with id: {component_or_id}")
                return
        else:
            raise TypeError("Input should be either a PageComponent instance or a component id string")

        if component in self._children:
            self._children.remove(component)
            del component
        else:
            print(f"Component: {component.title} not in page: {self.title}")

    def add_components(self, components):
        for component in components:
            if isinstance(component, PageComponent):
                if component not in self._children:
                    self._children.append(component)
                # Set the parent of the component to this page if it's not already set
                if component.parent is None and component.parent != self:
                    component.parent = self
            else:
                raise ValueError("The components should be of type PageComponent")

    def add_graph_component(self, title, component_id, figure, show_title=True):
        graph_component = PageComponent.plotly_figure(title, component_id, figure, show_title)
        self.add_component(graph_component)

    def add_img_component(self, title, src):
        img_component = PageComponent.img(title, src)
        self.add_component(img_component)

    def add_image_slider_component(self, title, component_id, images, captions=None):
        image_slider_component = PageComponent.image_slider(title, component_id, images, captions)
        self.add_component(image_slider_component)

    def add_div_child(self, child):
        self._children.append(child)


class Dashboard:
    def __init__(self, title='Dashboard', assets_folder='/assets'):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
                             assets_folder=assets_folder)
        self.title = title
        self.current_path = '/'
        self.pages = []

    def add_page(self, page: Page):
        '''
        Add a page to the dashboard.
        The page should be of type Page
        '''
        if page not in self.pages:
            self.pages.append(page)
        # Set the dashboard of the page to this dashboard only if it's not already set
        if page.dashboard is None or page.dashboard != self:
            page.dashboard = self

    def remove_page(self, page):
        """
        Remove a page from the dashboard
        :param page: Page, the page to be removed
        Returns:
        """
        if page in self.pages:
            self.pages.remove(page)
            page.dashboard = None
        else:
            print(f"Page: {page.title} not in Dashboard: {self.title}")

    def add_pages(self, pages):
        '''
        Add a list of pages to the dashboard. The pages should be of type Page
        '''
        for page in pages:
            if isinstance(page, Page):
                if page not in self.pages:
                    self.pages.append(page)
                # Set the dashboard of the page to this dashboard only if it's not already set
                if page.dashboard is None or page.dashboard != self:
                    page.dashboard = self
            else:
                raise ValueError("The pages should be of type Page")

    def navbar(self):
        navbar = dbc.NavbarSimple(
            children=[dbc.NavItem(dbc.NavLink(page.title, href=page.href)) for page in self.pages],
            brand=self.title,
            brand_href="/",
            sticky="top",
        )
        return navbar

    def layout(self):
        layout = html.Div([
            dcc.Location(id='url', refresh=False),
            self.navbar(),
            html.Div(id='breadcrumb-container', style={
                "margin": "0px",  # Adjust based on the height of your navbar
                "padding-left": "10px",
                "font-size": "14px",
            }),
            html.Div(id='page-content')
        ])
        return layout

    def recursive_fetch_page(self, pathname, page):
        if pathname == page.href:
            return page.layout()
        for subpage in page.subpages:
            if pathname == subpage.href:
                return subpage.layout()
            else:
                layout = self.recursive_fetch_page(pathname, subpage)
                if layout is not None:
                    return layout
        return None

    def callback(self):
        @self.app.callback(Output('page-content', 'children'),
                           [Input('url', 'pathname')])
        def display_page(pathname):
            print("Dashboard app Callback")
            for page in self.pages:
                layout = self.recursive_fetch_page(pathname, page)
                if layout is not None:
                    self.current_path = pathname
                    return layout
            print("Page not found. Pathname: ", pathname)

        @self.app.callback(Output('breadcrumb-container', 'children'),
                           [Input('url', 'pathname')])
        def display_breadcrumb(pathname):
            if pathname == '/':
                return html.Div()

            # Split the pathname and build the breadcrumb
            path_parts = pathname.strip('/').split('/')
            breadcrumbs = [{"label": "Home", "href": "/"}]

            for i in range(len(path_parts)):
                # Build the link for the current breadcrumb item
                href = '/' + '/'.join(path_parts[:i + 1])
                if i == len(path_parts) - 1:
                    # Current page, no link
                    breadcrumbs.append({"label": path_parts[i], "active": True})
                else:
                    # Previous pages, with links
                    breadcrumbs.append({"label": path_parts[i], "href": href})

            return dbc.Breadcrumb(items=breadcrumbs)

        for page in self.pages:
            page.register_callbacks(self.app)

    def run(self, debug=False):
        self.app.layout = self.layout()
        self.callback()
        self.app.run_server(debug=debug)
        print("Dashboard running")


if __name__ == '__main__':
    dashboard = Dashboard()

    # dashboard.add_page(Page('Index Page', '/', [Page.plotly_figure('graph-1', {'x': [1, 2, 4], 'y': [1, 5, 1]}), Page.img("/assets/traj_plot.png"), Page.image_slider('image-slider', ["/assets/images/data_V101/1403715273262142976.png", "/assets/images/data_V101/1403715390062142976.png", "/assets/traj_plot.png"])]))
    # dashboard.add_page(Page('Page 2', '/page-2', [Page.plotly_figure('graph-2', {'x': [1, 2, 3], 'y': [1, 3, 1]}), Page.img("https://plotly.com/all_static/images/plotly_graph.png")]))
    # dashboard.add_page(Page('Page 3', '/page-3', [Page.plotly_figure('graph-3', {'x': [1, 2, 3], 'y': [1, 3, 1]}), Page.img("https://plotly.com/all_static/images/plotly_graph.png")]))
    dashboard.run(debug=True)
